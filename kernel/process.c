#include <stdint.h>
#include "process.h"
#include "vmm.h"
#include "pmm.h"
#include "sched.h"
#include "serial.h"
#include "string.h"

struct thread *process_create(const void *binary, uint64_t size) {
    uint64_t cr3 = vmm_create_address_space();
    if (!cr3) {
        serial_puts("PROC: OOM (addr space)\n");
        return NULL;
    }

    /* Map binary pages at USER_CODE_BASE */
    uint64_t pages = (size + 4095) / 4096;
    for (uint64_t i = 0; i < pages; i++) {
        uint64_t paddr = pmm_alloc_page();
        if (!paddr) return NULL;

        uint64_t vaddr = USER_CODE_BASE + i * 4096;
        uint64_t offset = i * 4096;
        uint64_t copy_len = size - offset;
        if (copy_len > 4096) copy_len = 4096;

        uint8_t *dst = (uint8_t *)phys_to_virt(paddr);
        memcpy(dst, (const uint8_t *)binary + offset, copy_len);
        if (copy_len < 4096)
            memset(dst + copy_len, 0, 4096 - copy_len);

        vmm_map_page(cr3, vaddr, paddr, PAGE_PRESENT | PAGE_WRITE | PAGE_USER);
    }

    /* Map user stack page */
    uint64_t stack_phys = pmm_alloc_page();
    if (!stack_phys) return NULL;
    memset(phys_to_virt(stack_phys), 0, 4096);
    vmm_map_page(cr3, USER_STACK_BASE, stack_phys,
                 PAGE_PRESENT | PAGE_WRITE | PAGE_USER);

    uint64_t user_stack_top = USER_STACK_BASE + USER_STACK_SIZE;
    struct thread *t = thread_create_user(cr3, USER_CODE_BASE, user_stack_top);
    if (!t) return NULL;

    serial_puts("PROC: created pid=");
    serial_put_hex(t->tid);
    serial_putc('\n');

    return t;
}
