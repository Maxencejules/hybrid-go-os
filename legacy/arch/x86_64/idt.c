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
#define GATE_USER   0xEE   /* Present, DPL=3, interrupt gate */

static struct idt_entry idt[IDT_ENTRIES] __attribute__((aligned(16)));
static struct idtr idtr;

/* ISR stub table (defined in isr.asm) */
extern uint64_t isr_stub_table[48];

/* Syscall stub (defined in isr.asm) */
extern void syscall_stub(void);

/* Assembly helper (defined in isr.asm) */
extern void idt_flush(struct idtr *idtr_ptr);

/* ------------------------------------------------------------------ */
/*  idt_set_gate                                                      */
/* ------------------------------------------------------------------ */

static void idt_set_gate_attr(int n, uint64_t handler, uint8_t ist, uint8_t type_attr) {
    idt[n].offset_low  = (uint16_t)(handler & 0xFFFF);
    idt[n].selector    = KERNEL_CS;
    idt[n].ist         = ist & 0x7;
    idt[n].type_attr   = type_attr;
    idt[n].offset_mid  = (uint16_t)((handler >> 16) & 0xFFFF);
    idt[n].offset_hi   = (uint32_t)(handler >> 32);
    idt[n].reserved    = 0;
}

static void idt_set_gate(int n, uint64_t handler, uint8_t ist) {
    idt_set_gate_attr(n, handler, ist, GATE_INT);
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
        uint8_t ist = (i == 8) ? 1 : 0;   /* Double fault -> IST1 */
        idt_set_gate(i, isr_stub_table[i], ist);
    }

    /* Wire up the 16 IRQ stubs (vectors 32-47) */
    for (int i = 32; i < 48; i++) {
        idt_set_gate(i, isr_stub_table[i], 0);
    }

    /* Vector 0x80: syscall gate (DPL=3 so ring 3 can invoke) */
    idt_set_gate_attr(0x80, (uint64_t)syscall_stub, 0, GATE_USER);

    /* Load IDT */
    idtr.limit = sizeof(idt) - 1;
    idtr.base  = (uint64_t)&idt;
    idt_flush(&idtr);

    serial_puts("ARCH: IDT loaded\n");
}
