#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "serial.h"

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

__attribute__((used, section(".limine_requests_end")))
static volatile uint64_t limine_requests_end_marker[2] = {
    0xadc0e0531bb10d03, 0x9572709f31764c62
};

/* ------------------------------------------------------------------ */
/*  Kernel entry                                                      */
/* ------------------------------------------------------------------ */

#define DEBUG_EXIT_PORT 0xF4

void kmain(void) {
    /* Verify Limine accepted our base revision (zeroes element [2]). */
    if (limine_base_revision[2] != 0) {
        for (;;)
            __asm__ volatile ("cli; hlt");
    }

    serial_init();
    serial_puts("KERNEL: boot ok\n");
    serial_puts("KERNEL: halt ok\n");

    /* Exit QEMU via isa-debug-exit (value N -> exit code (N<<1)|1). */
    outb(DEBUG_EXIT_PORT, 0x00);

    for (;;)
        __asm__ volatile ("cli; hlt");
}
