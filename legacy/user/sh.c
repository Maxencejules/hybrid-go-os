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

/* Buffer to hold loaded binary — static global to save stack */
static uint8_t bin_buf[2048];

void main(void) {
    my_port = sys_ipc_create_port();

    /* Wait for fsd service */
    fsd_port = 0;
    while (fsd_port == 0) {
        fsd_port = sys_service_lookup("fsd");
        if (fsd_port == 0) sys_yield();
    }

    /* Spin-wait for "hello" file (pkg installs it) */
    struct fs_request req;
    struct fs_response resp;
    uint8_t fd = 0;
    uint32_t total_size = 0;

    for (;;) {
        zero128(&req);
        req.op = FS_OP_OPEN;
        req.data[0]='h'; req.data[1]='e'; req.data[2]='l'; req.data[3]='l';
        req.data[4]='o'; req.data[5]='\0';
        fs_send_recv(&req, &resp);

        if (resp.status == FS_OK) {
            fd = resp.data[0];
            total_size = resp.total_size;
            break;
        }
        sys_yield();
    }

    /* Read file contents into bin_buf */
    uint32_t read_offset = 0;
    while (read_offset < total_size && read_offset < 2048) {
        zero128(&req);
        req.op     = FS_OP_READ;
        req.fd     = fd;
        req.offset = read_offset;
        req.size   = 116;
        fs_send_recv(&req, &resp);

        if (resp.status != FS_OK || resp.size == 0) break;
        for (uint32_t i = 0; i < resp.size && read_offset + i < 2048; i++)
            bin_buf[read_offset + i] = resp.data[i];
        read_offset += resp.size;
    }

    /* Spawn the loaded binary as a new process */
    int64_t tid = sys_process_spawn(bin_buf, total_size);
    if (tid < 0)
        sys_debug_write("SH: spawn fail\n", 15);

    for (;;) sys_yield();
}
