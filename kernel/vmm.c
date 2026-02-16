#include <stdint.h>
#include <stddef.h>
#include "vmm.h"
#include "pmm.h"
#include "limine.h"
#include "serial.h"
#include "string.h"

extern struct limine_hhdm_request hhdm_request;

uint64_t hhdm_offset = 0;
uint64_t kernel_cr3 = 0;

static inline uint64_t read_cr3(void) {
    uint64_t val;
    __asm__ volatile ("mov %%cr3, %0" : "=r"(val));
    return val;
}

void vmm_init(void) {
    if (!hhdm_request.response) {
        serial_puts("VMM: no HHDM\n");
        for (;;) __asm__ volatile ("cli; hlt");
    }

    hhdm_offset = hhdm_request.response->offset;
    kernel_cr3 = read_cr3();

    serial_puts("VMM: initialized\n");
}

uint64_t vmm_create_address_space(void) {
    uint64_t pml4_phys = pmm_alloc_page();
    if (!pml4_phys) return 0;

    uint64_t *pml4 = (uint64_t *)phys_to_virt(pml4_phys);
    memset(pml4, 0, 4096);

    /* Copy upper half (kernel mappings) from current PML4 */
    uint64_t *kpml4 = (uint64_t *)phys_to_virt(kernel_cr3 & PTE_ADDR_MASK);
    for (int i = 256; i < 512; i++)
        pml4[i] = kpml4[i];

    return pml4_phys;
}

int vmm_map_page(uint64_t cr3, uint64_t vaddr, uint64_t paddr, uint64_t flags) {
    uint64_t *pml4 = (uint64_t *)phys_to_virt(cr3 & PTE_ADDR_MASK);

    int i4 = (vaddr >> 39) & 0x1FF;
    int i3 = (vaddr >> 30) & 0x1FF;
    int i2 = (vaddr >> 21) & 0x1FF;
    int i1 = (vaddr >> 12) & 0x1FF;

    /* PML4 → PDPT */
    if (!(pml4[i4] & PAGE_PRESENT)) {
        uint64_t p = pmm_alloc_page();
        if (!p) return -1;
        memset(phys_to_virt(p), 0, 4096);
        pml4[i4] = p | PAGE_PRESENT | PAGE_WRITE | PAGE_USER;
    }
    uint64_t *pdpt = (uint64_t *)phys_to_virt(pml4[i4] & PTE_ADDR_MASK);

    /* PDPT → PD */
    if (!(pdpt[i3] & PAGE_PRESENT)) {
        uint64_t p = pmm_alloc_page();
        if (!p) return -1;
        memset(phys_to_virt(p), 0, 4096);
        pdpt[i3] = p | PAGE_PRESENT | PAGE_WRITE | PAGE_USER;
    }
    uint64_t *pd = (uint64_t *)phys_to_virt(pdpt[i3] & PTE_ADDR_MASK);

    /* PD → PT */
    if (!(pd[i2] & PAGE_PRESENT)) {
        uint64_t p = pmm_alloc_page();
        if (!p) return -1;
        memset(phys_to_virt(p), 0, 4096);
        pd[i2] = p | PAGE_PRESENT | PAGE_WRITE | PAGE_USER;
    }
    uint64_t *pt = (uint64_t *)phys_to_virt(pd[i2] & PTE_ADDR_MASK);

    pt[i1] = (paddr & PTE_ADDR_MASK) | flags;
    return 0;
}
