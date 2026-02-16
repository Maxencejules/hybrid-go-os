#ifndef VMM_H
#define VMM_H

#include <stdint.h>

#define PAGE_PRESENT  (1ULL << 0)
#define PAGE_WRITE    (1ULL << 1)
#define PAGE_USER     (1ULL << 2)

#define PTE_ADDR_MASK 0x000FFFFFFFFFF000ULL

extern uint64_t kernel_cr3;
extern uint64_t hhdm_offset;

static inline void *phys_to_virt(uint64_t paddr) {
    return (void *)(paddr + hhdm_offset);
}

void     vmm_init(void);
uint64_t vmm_create_address_space(void);
int      vmm_map_page(uint64_t cr3, uint64_t vaddr, uint64_t paddr, uint64_t flags);

#endif
