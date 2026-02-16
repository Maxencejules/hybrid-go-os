#include "syscall.h"

static uint32_t compute_checksum(const volatile uint8_t *data, uint32_t len) {
    uint32_t sum = 0;
    for (uint32_t i = 0; i < len; i++)
        sum += data[i];
    return sum;
}

void main(void) {
    /* Create port and register as "shm_reader" */
    uint32_t my_port = sys_ipc_create_port();
    sys_service_register("shm_reader", my_port);

    /* Wait for writer to send handle + checksum */
    char msg[128];
    uint32_t sender;
    sys_ipc_recv(my_port, msg, &sender);

    uint32_t handle = *(uint32_t *)(msg + 0);
    uint32_t expected = *(uint32_t *)(msg + 4);

    /* Map the shared memory region */
    uint64_t vaddr = sys_shm_map(handle, 0);
    if (vaddr == 0) {
        sys_debug_write("SHM: map failed\n", 16);
        for (;;) sys_yield();
    }

    /* Verify checksum */
    volatile uint8_t *shm = (volatile uint8_t *)vaddr;
    uint32_t actual = compute_checksum(shm, 4096);

    if (actual == expected) {
        sys_debug_write("SHM: checksum ok\n", 17);
    } else {
        sys_debug_write("SHM: checksum mismatch\n", 23);
    }

    for (;;)
        sys_yield();
}
