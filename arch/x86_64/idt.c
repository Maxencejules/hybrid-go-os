#include <stdint.h>
#include <stddef.h>
#include "../../kernel/serial.h"

/* ------------------------------------------------------------------ */
/*  IDT entry (16 bytes in long mode)                                 */
/* ------------------------------------------------------------------ */

struct idt_entry {
    uint16_t offset_low;
    uint16_t selector;
    uint8_t  ist;          /* bits 0-2 = IST index, rest 0 */
    uint8_t  type_attr;    /* type + DPL + P */
    uint16_t offset_mid;
    uint32_t offset_hi;
    uint32_t reserved;
} __attribute__((packed));

struct idtr {
    uint16_t limit;
    uint64_t base;
} __attribute__((packed));

#define IDT_ENTRIES 256
#define KERNEL_CS   0x08
#define GATE_INT    0x8E   /* Present, DPL=0, interrupt gate */

static struct idt_entry idt[IDT_ENTRIES] __attribute__((aligned(16)));
static struct idtr idtr;

/* ISR stub table (defined in isr.asm) */
extern uint64_t isr_stub_table[32];

/* Assembly helper (defined in isr.asm) */
extern void idt_flush(struct idtr *idtr_ptr);

/* ------------------------------------------------------------------ */
/*  idt_set_gate                                                      */
/* ------------------------------------------------------------------ */

static void idt_set_gate(int n, uint64_t handler, uint8_t ist) {
    idt[n].offset_low  = (uint16_t)(handler & 0xFFFF);
    idt[n].selector    = KERNEL_CS;
    idt[n].ist         = ist & 0x7;
    idt[n].type_attr   = GATE_INT;
    idt[n].offset_mid  = (uint16_t)((handler >> 16) & 0xFFFF);
    idt[n].offset_hi   = (uint32_t)(handler >> 32);
    idt[n].reserved    = 0;
}

/* ------------------------------------------------------------------ */
/*  idt_init                                                          */
/* ------------------------------------------------------------------ */

void idt_init(void) {
    /* Zero all entries first */
    for (int i = 0; i < IDT_ENTRIES; i++) {
        idt[i] = (struct idt_entry){0};
    }

    /* Wire up the 32 CPU exception stubs */
    for (int i = 0; i < 32; i++) {
        uint8_t ist = (i == 8) ? 1 : 0;   /* Double fault → IST1 */
        idt_set_gate(i, isr_stub_table[i], ist);
    }

    /* Load IDT */
    idtr.limit = sizeof(idt) - 1;
    idtr.base  = (uint64_t)&idt;
    idt_flush(&idtr);

    serial_puts("ARCH: IDT loaded\n");
}
