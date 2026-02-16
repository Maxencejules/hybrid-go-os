#include "syscall.h"

static uint32_t compute_checksum(const volatile uint8_t *data, uint32_t len) {
    uint32_t sum = 0;
    for (uint32_t i = 0; i < len; i++)
        sum += data[i];
    return sum;
}

void main(void) {
    /* Retry until shm_reader service is registered */
    uint32_t reader_port = 0;
    while (reader_port == 0) {
        reader_port = sys_service_lookup("shm_reader");
        if (reader_port == 0)
            sys_yield();
    }

    /* Create shared memory region */
    uint32_t handle = sys_shm_create(4096);
    if (handle == 0) {
        sys_debug_write("SHM: create failed\n", 19);
        for (;;) sys_yield();
    }

    /* Map it into our address space */
    uint64_t vaddr = sys_shm_map(handle, 0);
    if (vaddr == 0) {
        sys_debug_write("SHM: map failed\n", 16);
        for (;;) sys_yield();
    }

    /* Fill with pattern */
    volatile uint8_t *shm = (volatile uint8_t *)vaddr;
    for (uint32_t i = 0; i < 4096; i++)
        shm[i] = (uint8_t)(i & 0xFF);

    /* Compute checksum */
    uint32_t checksum = compute_checksum(shm, 4096);

    /* Send handle + checksum to reader via IPC */
    char msg[8];
    *(uint32_t *)(msg + 0) = handle;
    *(uint32_t *)(msg + 4) = checksum;
    sys_ipc_send(reader_port, msg, 8);

    for (;;)
        sys_yield();
}
