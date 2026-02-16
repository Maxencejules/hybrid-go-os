#include <stdint.h>
#include "../../kernel/serial.h"
#include "idt.h"
#include "trap.h"

static inline uint64_t read_cr2(void) {
    uint64_t val;
    __asm__ volatile ("mov %%cr2, %0" : "=r"(val));
    return val;
}

void trap_handler(struct interrupt_frame *frame) {
    uint64_t int_num = frame->int_num;

    if (int_num == 14) {
        /* Page fault */
        uint64_t cr2 = read_cr2();
        serial_puts("PF: addr=0x");
        serial_put_hex(cr2);
        serial_puts(" err=0x");
        serial_put_hex(frame->error_code);
        serial_putc('\n');

        if (pf_recovery_rip != 0) {
            frame->rip = pf_recovery_rip;
            pf_recovery_rip = 0;
            return;
        }
    } else if (int_num == 8) {
        serial_puts("FATAL: double fault\n");
    } else if (int_num == 13) {
        serial_puts("FATAL: GPF err=0x");
        serial_put_hex(frame->error_code);
        serial_putc('\n');
    } else {
        serial_puts("TRAP: int=0x");
        serial_put_hex(int_num);
        serial_putc('\n');
    }

    /* Unrecoverable: halt */
    for (;;)
        __asm__ volatile ("cli; hlt");
}
