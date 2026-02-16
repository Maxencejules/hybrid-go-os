#include "syscall.h"
#include "fs_protocol.h"

/* ---- On-disk structures (match SimpleFS layout) ---- */

struct sfs_superblock {
    uint32_t magic;
    uint32_t file_count;
    uint32_t data_start;
    uint32_t next_free;
};

struct sfs_file_entry {
    char     name[24];
    uint32_t start_sector;
    uint32_t size_bytes;
};

/* ---- Global state (BSS — zeroed by process_create page-tail clearing) ---- */

static struct sfs_superblock superblock;
static struct sfs_file_entry file_table[16];
static uint8_t sector_buf[512];

/* ---- Helpers ---- */

static int streq(const char *a, const char *b) {
    for (int i = 0; i < 24; i++) {
        if (a[i] != b[i]) return 0;
        if (a[i] == '\0') return 1;
    }
    return 1;
}

static void zero128(void *p) {
    uint8_t *b = (uint8_t *)p;
    for (int i = 0; i < 128; i++) b[i] = 0;
}

/* ---- Flush superblock + file table to disk ---- */

static void flush_metadata(void) {
    /* Superblock → sector 0 */
    for (int i = 0; i < 512; i++) sector_buf[i] = 0;
    uint32_t *sb = (uint32_t *)sector_buf;
    sb[0] = superblock.magic;
    sb[1] = superblock.file_count;
    sb[2] = superblock.data_start;
    sb[3] = superblock.next_free;
    sys_blk_write(0, sector_buf, 1);

    /* File table → sector 1 */
    for (int i = 0; i < 512; i++) sector_buf[i] = 0;
    for (int i = 0; i < 16; i++) {
        uint8_t *entry = sector_buf + i * 32;
        for (int j = 0; j < 24; j++)
            entry[j] = (uint8_t)file_table[i].name[j];
        uint32_t *fields = (uint32_t *)(entry + 24);
        fields[0] = file_table[i].start_sector;
        fields[1] = file_table[i].size_bytes;
    }
    sys_blk_write(1, sector_buf, 1);
}

/* ---- Main ---- */

void main(void) {
    /* 1. Read superblock from sector 0 */
    sys_blk_read(0, sector_buf, 1);
    uint32_t *sb = (uint32_t *)sector_buf;
    superblock.magic      = sb[0];
    superblock.file_count = sb[1];
    superblock.data_start = sb[2];
    superblock.next_free  = sb[3];

    if (superblock.magic != SFS_MAGIC) {
        sys_debug_write("FSD: bad magic\n", 15);
        for (;;) sys_yield();
    }

    /* 2. Read file table from sector 1 */
    sys_blk_read(1, sector_buf, 1);
    for (int i = 0; i < 16; i++) {
        uint8_t *entry = sector_buf + i * 32;
        for (int j = 0; j < 24; j++)
            file_table[i].name[j] = (char)entry[j];
        uint32_t *fields = (uint32_t *)(entry + 24);
        file_table[i].start_sector = fields[0];
        file_table[i].size_bytes   = fields[1];
    }

    sys_debug_write("FSD: mount ok\n", 14);

    /* 3. Register as service */
    uint32_t my_port = sys_ipc_create_port();
    sys_service_register("fsd", my_port);

    /* 4. IPC request loop */
    for (;;) {
        struct fs_request req;
        uint32_t sender;
        sys_ipc_recv(my_port, &req, &sender);

        struct fs_response resp;
        zero128(&resp);

        switch (req.op) {

        case FS_OP_OPEN: {
            int found = -1;
            for (int i = 0; i < (int)superblock.file_count; i++) {
                if (streq(file_table[i].name, req.data)) {
                    found = i;
                    break;
                }
            }
            if (found >= 0) {
                resp.status     = FS_OK;
                resp.total_size = file_table[found].size_bytes;
                resp.data[0]    = (uint8_t)found;   /* fd */
            } else {
                resp.status = FS_NOT_FOUND;
            }
            sys_ipc_send(req.reply_port, &resp, 128);
            break;
        }

        case FS_OP_READ: {
            int idx = req.fd;
            if (idx < 0 || idx >= (int)superblock.file_count) {
                resp.status = FS_ERR;
                sys_ipc_send(req.reply_port, &resp, 128);
                break;
            }
            uint32_t fsize = file_table[idx].size_bytes;
            uint32_t off   = req.offset;
            if (off >= fsize) {
                resp.status = FS_OK;
                resp.size   = 0;
                sys_ipc_send(req.reply_port, &resp, 128);
                break;
            }
            uint32_t avail   = fsize - off;
            uint32_t to_read = req.size;
            if (to_read > avail) to_read = avail;
            if (to_read > 116)   to_read = 116;

            uint32_t start_sec  = file_table[idx].start_sector;
            uint32_t sec_offset = off / 512;
            uint32_t byte_in_sec = off % 512;

            sys_blk_read(start_sec + sec_offset, sector_buf, 1);

            uint32_t copied = 0;
            while (copied < to_read) {
                uint32_t chunk = 512 - byte_in_sec;
                if (chunk > to_read - copied) chunk = to_read - copied;
                for (uint32_t i = 0; i < chunk; i++)
                    resp.data[copied + i] = sector_buf[byte_in_sec + i];
                copied += chunk;
                byte_in_sec = 0;
                if (copied < to_read) {
                    sec_offset++;
                    sys_blk_read(start_sec + sec_offset, sector_buf, 1);
                }
            }

            resp.status     = FS_OK;
            resp.size       = copied;
            resp.total_size = fsize;
            sys_ipc_send(req.reply_port, &resp, 128);
            break;
        }

        case FS_OP_CREATE: {
            if (superblock.file_count >= 16) {
                resp.status = FS_ERR;
                sys_ipc_send(req.reply_port, &resp, 128);
                break;
            }
            int idx = (int)superblock.file_count;
            for (int j = 0; j < 24; j++)
                file_table[idx].name[j] = req.data[j];
            file_table[idx].start_sector = superblock.next_free;
            file_table[idx].size_bytes   = 0;
            superblock.file_count++;

            resp.status  = FS_OK;
            resp.data[0] = (uint8_t)idx;   /* fd */
            sys_ipc_send(req.reply_port, &resp, 128);
            break;
        }

        case FS_OP_WRITE: {
            int idx = req.fd;
            if (idx < 0 || idx >= (int)superblock.file_count || req.size > 112) {
                resp.status = FS_ERR;
                sys_ipc_send(req.reply_port, &resp, 128);
                break;
            }
            uint32_t fsize      = file_table[idx].size_bytes;
            uint32_t start_sec  = file_table[idx].start_sector;
            uint32_t sec_idx    = fsize / 512;
            uint32_t byte_in_sec = fsize % 512;

            /* Read current partial sector if appending mid-sector */
            if (byte_in_sec > 0)
                sys_blk_read(start_sec + sec_idx, sector_buf, 1);
            else
                for (int i = 0; i < 512; i++) sector_buf[i] = 0;

            uint32_t written = 0;
            while (written < req.size) {
                uint32_t chunk = 512 - byte_in_sec;
                if (chunk > req.size - written) chunk = req.size - written;
                for (uint32_t i = 0; i < chunk; i++)
                    sector_buf[byte_in_sec + i] = (uint8_t)req.data[written + i];
                written += chunk;

                sys_blk_write(start_sec + sec_idx, sector_buf, 1);

                byte_in_sec = 0;
                sec_idx++;
                if (written < req.size)
                    for (int i = 0; i < 512; i++) sector_buf[i] = 0;
            }

            file_table[idx].size_bytes = fsize + req.size;
            uint32_t end_sec = start_sec + (file_table[idx].size_bytes + 511) / 512;
            if (end_sec > superblock.next_free)
                superblock.next_free = end_sec;

            flush_metadata();

            resp.status = FS_OK;
            resp.size   = req.size;
            sys_ipc_send(req.reply_port, &resp, 128);
            break;
        }

        default:
            resp.status = FS_ERR;
            sys_ipc_send(req.reply_port, &resp, 128);
            break;
        }
    }
}
