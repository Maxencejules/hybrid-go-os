#include "syscall.h"
#include "fs_protocol.h"

static uint32_t fsd_port;
static uint32_t my_port;

static void zero128(void *p) {
    uint8_t *b = (uint8_t *)p;
    for (int i = 0; i < 128; i++) b[i] = 0;
}

static void fs_send_recv(struct fs_request *req, struct fs_response *resp) {
    req->reply_port = my_port;
    sys_ipc_send(fsd_port, req, 128);
    uint32_t sender;
    sys_ipc_recv(my_port, resp, &sender);
}

/* Buffer to hold entire package contents (header + binary) */
static uint8_t pkg_buf[1024];

void main(void) {
    my_port = sys_ipc_create_port();

    /* Wait for fsd service */
    fsd_port = 0;
    while (fsd_port == 0) {
        fsd_port = sys_service_lookup("fsd");
        if (fsd_port == 0) sys_yield();
    }

    /* 1. Open hello.pkg */
    struct fs_request req;
    struct fs_response resp;
    zero128(&req);

    req.op = FS_OP_OPEN;
    /* Copy "hello.pkg" into req.data */
    req.data[0]='h'; req.data[1]='e'; req.data[2]='l'; req.data[3]='l';
    req.data[4]='o'; req.data[5]='.'; req.data[6]='p'; req.data[7]='k';
    req.data[8]='g'; req.data[9]='\0';
    fs_send_recv(&req, &resp);

    if (resp.status != FS_OK) {
        sys_debug_write("PKG: open fail\n", 15);
        for (;;) sys_yield();
    }

    uint8_t fd = resp.data[0];
    uint32_t total_size = resp.total_size;

    /* 2. Read entire package into pkg_buf */
    uint32_t read_offset = 0;
    while (read_offset < total_size && read_offset < 1024) {
        zero128(&req);
        req.op     = FS_OP_READ;
        req.fd     = fd;
        req.offset = read_offset;
        req.size   = 116;
        fs_send_recv(&req, &resp);

        if (resp.status != FS_OK || resp.size == 0) break;
        for (uint32_t i = 0; i < resp.size && read_offset + i < 1024; i++)
            pkg_buf[read_offset + i] = resp.data[i];
        read_offset += resp.size;
    }

    /* 3. Parse PKG header (first 32 bytes) */
    uint32_t magic    = *(uint32_t *)(pkg_buf + 0);
    uint32_t bin_size = *(uint32_t *)(pkg_buf + 4);
    /* App name at pkg_buf+8, 24 bytes */

    if (magic != PKG_MAGIC) {
        sys_debug_write("PKG: bad magic\n", 15);
        for (;;) sys_yield();
    }

    /* 4. Create file with extracted name */
    zero128(&req);
    req.op = FS_OP_CREATE;
    for (int j = 0; j < 24; j++)
        req.data[j] = (char)pkg_buf[8 + j];
    fs_send_recv(&req, &resp);

    if (resp.status != FS_OK) {
        sys_debug_write("PKG: create fail\n", 17);
        for (;;) sys_yield();
    }
    uint8_t new_fd = resp.data[0];

    /* 5. Write binary data in 112-byte chunks */
    uint8_t *bin_data = pkg_buf + 32;
    uint32_t written = 0;
    while (written < bin_size) {
        zero128(&req);
        req.op = FS_OP_WRITE;
        req.fd = new_fd;
        uint32_t chunk = bin_size - written;
        if (chunk > 112) chunk = 112;
        req.size = chunk;
        for (uint32_t i = 0; i < chunk; i++)
            req.data[i] = (char)bin_data[written + i];
        fs_send_recv(&req, &resp);

        if (resp.status != FS_OK) {
            sys_debug_write("PKG: write fail\n", 16);
            for (;;) sys_yield();
        }
        written += chunk;
    }

    sys_debug_write("PKG: hello installed\n", 21);

    for (;;) sys_yield();
}
