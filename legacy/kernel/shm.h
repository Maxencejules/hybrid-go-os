#ifndef SHM_H
#define SHM_H

#include <stdint.h>

#define MAX_SHM_REGIONS 16
#define SHM_MAP_VADDR   0x10000000ULL

struct shm_region {
    uint32_t handle;
    uint64_t paddr;
    uint64_t size;
};

void     shm_init(void);
uint32_t shm_create(uint64_t size);
uint64_t shm_map(uint32_t handle, uint64_t vaddr_hint);

#endif
