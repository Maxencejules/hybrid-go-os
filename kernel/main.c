#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "serial.h"
#include "limine.h"
#include "pmm.h"
#include "sched.h"
#include "../arch/x86_64/gdt.h"
#include "../arch/x86_64/idt.h"
#include "../arch/x86_64/trap.h"
#include "../arch/x86_64/pic.h"
#include "../arch/x86_64/pit.h"

/* ------------------------------------------------------------------ */
/*  Limine boot-protocol markers (v8 API, raw magic values)            */
/* ------------------------------------------------------------------ */

__attribute__((used, section(".limine_requests_start")))
static volatile uint64_t limine_requests_start_marker[4] = {
    0xf6b8f4b39de7d1ae, 0xfab91a6940fcb9cf,
    0x785c6ed015d3e316, 0x181e920a7852b9d9
};

__attribute__((used, section(".limine_requests")))
static volatile uint64_t limine_base_revision[3] = {
    0xf9562b2d5c95a6c8, 0x6a7b384944536bdc, 3
};

/* Memory map request */
__attribute__((used, section(".limine_requests")))
struct limine_memmap_request memmap_request = {
    .id = {
        LIMINE_COMMON_MAGIC_0, LIMINE_COMMON_MAGIC_1,
        0x67cf3d9d378a806f, 0xe304acdfc50c3c62
    },
    .revision = 0,
    .response = NULL,
};

__attribute__((used, section(".limine_requests_end")))
static volatile uint64_t limine_requests_end_marker[2] = {
    0xadc0e0531bb10d03, 0x9572709f31764c62
};

/* ------------------------------------------------------------------ */
/*  Kernel entry                                                      */
/* ------------------------------------------------------------------ */

#define DEBUG_EXIT_PORT 0xF4

static inline uint64_t read_cr0(void) {
    uint64_t val;
    __asm__ volatile ("mov %%cr0, %0" : "=r"(val));
    return val;
}

static void thread_a(void) {
    for (;;)
        serial_putc('A');
}

static void thread_b(void) {
    for (;;)
        serial_putc('B');
}

void kmain(void) {
    /* Verify Limine accepted our base revision (zeroes element [2]). */
    if (limine_base_revision[2] != 0) {
        for (;;)
            __asm__ volatile ("cli; hlt");
    }

    serial_init();
    serial_puts("KERNEL: boot ok\n");

    gdt_init();
    idt_init();
    pmm_init();

    /* Verify paging is enabled (CR0 bit 31) */
    if (read_cr0() & (1ULL << 31))
        serial_puts("MM: paging=on\n");
    else
        serial_puts("MM: paging=off\n");

    /* Controlled page fault test */
    test_trigger_page_fault();

    /* M2: PIC, PIT, scheduler */
    pic_init();
    pit_init(100);
    sched_init();
    thread_create(thread_a);
    thread_create(thread_b);

    /* Enable interrupts — preemption begins */
    __asm__ volatile ("sti");

    /* Idle loop (kmain is the idle thread) */
    for (;;)
        __asm__ volatile ("hlt");
}
