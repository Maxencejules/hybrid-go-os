#ifndef IDT_H
#define IDT_H

#include <stdint.h>

struct interrupt_frame {
    /* GPRs saved by isr_common (pushed in reverse order) */
    uint64_t r15, r14, r13, r12, r11, r10, r9, r8;
    uint64_t rbp, rdi, rsi, rdx, rcx, rbx, rax;
    /* Pushed by ISR stub */
    uint64_t int_num;
    uint64_t error_code;
    /* Pushed by CPU on interrupt/exception */
    uint64_t rip;
    uint64_t cs;
    uint64_t rflags;
    uint64_t rsp;
    uint64_t ss;
};

void idt_init(void);

#endif
