#include <stdint.h>
#include "../../kernel/serial.h"
#include "../../kernel/sched.h"
#include "../../kernel/syscall.h"
#include "idt.h"
#include "trap.h"
#include "pic.h"

#define DEBUG_EXIT_PORT 0xF4

volatile uint64_t tick_count = 0;

static inline uint64_t read_cr2(void) {
    uint64_t val;
    __asm__ volatile ("mov %%cr2, %0" : "=r"(val));
    return val;
}

void trap_handler(struct interrupt_frame *frame) {
    uint64_t int_num = frame->int_num;

    /* Syscall: int 0x80 */
    if (int_num == 0x80) {
        syscall_handler(frame);
        return;
    }

    /* IRQ range: vectors 32-47 */
    if (int_num >= 32 && int_num <= 47) {
        uint8_t irq = (uint8_t)(int_num - 32);

        if (irq == 0) {
            /* Timer tick */
            tick_count++;

            if (tick_count == 100) {
                serial_puts("TICK: 100\n");
            } else if (tick_count == 400) {
                serial_puts("\nKERNEL: halt ok\n");
                outb(DEBUG_EXIT_PORT, 0x00);
            }

            pic_send_eoi(irq);
            schedule();
        } else {
            pic_send_eoi(irq);
        }

        return;
    }

    /* CPU exceptions */
    if (int_num == 14) {
        /* Page fault */
        uint64_t cr2 = read_cr2();
        serial_puts("PF: addr=0x");
        serial_put_hex(cr2);
        serial_puts(" err=0x");
        serial_put_hex(frame->error_code);
        serial_putc('\n');

        /* Recovery path for kernel test */
        if (pf_recovery_rip != 0) {
            frame->rip = pf_recovery_rip;
            pf_recovery_rip = 0;
            return;
        }

        /* User-mode page fault: kill the thread */
        if (frame->cs & 3) {
            serial_puts("USER: killed tid=");
            serial_put_hex(current_thread->tid);
            serial_putc('\n');
            current_thread->state = THREAD_DEAD;
            schedule();
            return;
        }
    } else if (int_num == 8) {
        serial_puts("FATAL: double fault\n");
    } else if (int_num == 13) {
        serial_puts("FATAL: GPF err=0x");
        serial_put_hex(frame->error_code);
        serial_putc('\n');

        /* User-mode GPF: kill the thread */
        if (frame->cs & 3) {
            serial_puts("USER: killed tid=");
            serial_put_hex(current_thread->tid);
            serial_putc('\n');
            current_thread->state = THREAD_DEAD;
            schedule();
            return;
        }
    } else {
        serial_puts("TRAP: int=0x");
        serial_put_hex(int_num);
        serial_putc('\n');
    }

    /* Unrecoverable: halt */
    for (;;)
        __asm__ volatile ("cli; hlt");
}
