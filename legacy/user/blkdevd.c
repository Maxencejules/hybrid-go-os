#include "syscall.h"

void main(void) {
    /* Self-test: write pattern to sector 1000, read back, verify
     * (uses sector 1000 to avoid corrupting SimpleFS metadata at sectors 0-1) */
    uint8_t wbuf[512];
    uint8_t rbuf[512];

    for (int i = 0; i < 512; i++)
        wbuf[i] = (uint8_t)(i & 0xFF);

    int64_t ret = sys_blk_write(1000, wbuf, 1);
    if (ret != 0) {
        sys_debug_write("BLK: write fail\n", 16);
        for (;;) sys_yield();
    }

    for (int i = 0; i < 512; i++)
        rbuf[i] = 0;

    ret = sys_blk_read(1000, rbuf, 1);
    if (ret != 0) {
        sys_debug_write("BLK: read fail\n", 15);
        for (;;) sys_yield();
    }

    int ok = 1;
    for (int i = 0; i < 512; i++) {
        if (rbuf[i] != (uint8_t)(i & 0xFF)) {
            ok = 0;
            break;
        }
    }

    if (ok)
        sys_debug_write("BLK: rw ok\n", 11);
    else
        sys_debug_write("BLK: verify fail\n", 17);

    /* Register as IPC service for future M6 use */
    uint32_t port = sys_ipc_create_port();
    if (port != 0)
        sys_service_register("blkdev", port);

    for (;;)
        sys_yield();
}
