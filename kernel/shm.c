#include <stdint.h>
#include <stddef.h>
#include "shm.h"
#include "pmm.h"
#include "vmm.h"
#include "sched.h"
#include "serial.h"
#include "string.h"

static struct shm_region regions[MAX_SHM_REGIONS];
static uint32_t next_handle = 1;

void shm_init(void) {
    for (int i = 0; i < MAX_SHM_REGIONS; i++)
        regions[i].handle = 0;
    serial_puts("SHM: initialized\n");
}

uint32_t shm_create(uint64_t size) {
    if (size == 0 || size > 4096)
        return 0;

    for (int i = 0; i < MAX_SHM_REGIONS; i++) {
        if (regions[i].handle == 0) {
            uint64_t paddr = pmm_alloc_page();
            if (!paddr)
                return 0;
            memset(phys_to_virt(paddr), 0, 4096);

            regions[i].handle = next_handle++;
            regions[i].paddr = paddr;
            regions[i].size = 4096;
            return regions[i].handle;
        }
    }
    return 0;
}

uint64_t shm_map(uint32_t handle, uint64_t vaddr_hint) {
    if (handle == 0)
        return 0;

    for (int i = 0; i < MAX_SHM_REGIONS; i++) {
        if (regions[i].handle == handle) {
            uint64_t vaddr = vaddr_hint ? vaddr_hint : SHM_MAP_VADDR;
            uint64_t cr3 = current_thread->cr3;
            if (!cr3)
                cr3 = kernel_cr3;

            if (vmm_map_page(cr3, vaddr, regions[i].paddr,
                             PAGE_PRESENT | PAGE_WRITE | PAGE_USER) != 0)
                return 0;

            return vaddr;
        }
    }
    return 0;
}
