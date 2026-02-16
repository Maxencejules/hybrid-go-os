#ifndef PMM_H
#define PMM_H

#include <stdint.h>

#define PAGE_SIZE 4096

void     pmm_init(void);
uint64_t pmm_alloc_page(void);
void     pmm_free_page(uint64_t paddr);

#endif
