#ifndef PMM_H
#define PMM_H

#include <stdint.h>

#define PAGE_SIZE 4096

void     pmm_init(void);
uint64_t pmm_alloc_page(void);
uint64_t pmm_alloc_contiguous(uint32_t count);
void     pmm_free_page(uint64_t paddr);

#endif
