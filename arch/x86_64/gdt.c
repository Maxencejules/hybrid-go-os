#include <stdint.h>
#include <stddef.h>
#include "../../kernel/serial.h"

/* ------------------------------------------------------------------ */
/*  GDT entry                                                         */
/* ------------------------------------------------------------------ */

struct gdt_entry {
    uint16_t limit_low;
    uint16_t base_low;
    uint8_t  base_mid;
    uint8_t  access;
    uint8_t  flags_limit_hi;   /* flags (4 bits) | limit_hi (4 bits) */
    uint8_t  base_hi;
} __attribute__((packed));

/* TSS descriptor is 16 bytes (two GDT slots) in long mode. */
struct tss_entry {
    uint16_t limit_low;
    uint16_t base_low;
    uint8_t  base_mid;
    uint8_t  access;
    uint8_t  flags_limit_hi;
    uint8_t  base_hi;
    uint32_t base_upper;
    uint32_t reserved;
} __attribute__((packed));

struct gdtr {
    uint16_t limit;
    uint64_t base;
} __attribute__((packed));

/* ------------------------------------------------------------------ */
/*  TSS                                                               */
/* ------------------------------------------------------------------ */

struct tss {
    uint32_t reserved0;
    uint64_t rsp0;
    uint64_t rsp1;
    uint64_t rsp2;
    uint64_t reserved1;
    uint64_t ist1;
    uint64_t ist2;
    uint64_t ist3;
    uint64_t ist4;
    uint64_t ist5;
    uint64_t ist6;
    uint64_t ist7;
    uint64_t reserved2;
    uint16_t reserved3;
    uint16_t iopb_offset;
} __attribute__((packed));

/* Double-fault stack (4 KiB, in .bss) */
static uint8_t df_stack[4096] __attribute__((aligned(16)));

static struct tss tss;

/* ------------------------------------------------------------------ */
/*  GDT table (null + kcode + kdata + udata + ucode + TSS)            */
/* ------------------------------------------------------------------ */

/* 7 entries: null, kcode, kdata, udata, ucode, tss_lo, tss_hi */
static struct {
    struct gdt_entry entries[5];
    struct tss_entry tss;
} __attribute__((packed, aligned(16))) gdt;

static struct gdtr gdtr;

/* Assembly helpers (defined in isr.asm) */
extern void gdt_flush(struct gdtr *gdtr_ptr);

/* ------------------------------------------------------------------ */
/*  gdt_init                                                          */
/* ------------------------------------------------------------------ */

void gdt_init(void) {
    /* Entry 0: Null descriptor */
    gdt.entries[0] = (struct gdt_entry){0};

    /* Entry 1 (0x08): Kernel code — 64-bit, present, ring 0 */
    gdt.entries[1] = (struct gdt_entry){
        .limit_low     = 0xFFFF,
        .base_low      = 0,
        .base_mid      = 0,
        .access        = 0x9A,   /* P=1, DPL=0, S=1, Type=Execute/Read */
        .flags_limit_hi = 0x20 | 0x0F,  /* L=1 (64-bit), limit_hi=0xF */
        .base_hi       = 0,
    };

    /* Entry 2 (0x10): Kernel data — present, ring 0 */
    gdt.entries[2] = (struct gdt_entry){
        .limit_low     = 0xFFFF,
        .base_low      = 0,
        .base_mid      = 0,
        .access        = 0x92,   /* P=1, DPL=0, S=1, Type=Read/Write */
        .flags_limit_hi = 0x00 | 0x0F,  /* no L, no D/B for data */
        .base_hi       = 0,
    };

    /* Entry 3 (0x18): User data — present, ring 3 */
    gdt.entries[3] = (struct gdt_entry){
        .limit_low     = 0xFFFF,
        .base_low      = 0,
        .base_mid      = 0,
        .access        = 0xF2,   /* P=1, DPL=3, S=1, Type=Read/Write */
        .flags_limit_hi = 0x00 | 0x0F,
        .base_hi       = 0,
    };

    /* Entry 4 (0x20): User code — 64-bit, present, ring 3 */
    gdt.entries[4] = (struct gdt_entry){
        .limit_low     = 0xFFFF,
        .base_low      = 0,
        .base_mid      = 0,
        .access        = 0xFA,   /* P=1, DPL=3, S=1, Type=Execute/Read */
        .flags_limit_hi = 0x20 | 0x0F,  /* L=1 (64-bit), limit_hi=0xF */
        .base_hi       = 0,
    };

    /* TSS setup */
    tss = (struct tss){0};
    tss.ist1 = (uint64_t)(df_stack + sizeof(df_stack));
    tss.iopb_offset = sizeof(struct tss);

    uint64_t tss_base = (uint64_t)&tss;
    uint16_t tss_limit = sizeof(struct tss) - 1;

    /* Entry 5–6 (0x28): TSS descriptor (16 bytes) */
    gdt.tss = (struct tss_entry){
        .limit_low     = tss_limit,
        .base_low      = (uint16_t)(tss_base & 0xFFFF),
        .base_mid      = (uint8_t)((tss_base >> 16) & 0xFF),
        .access        = 0x89,   /* P=1, Type=Available 64-bit TSS */
        .flags_limit_hi = 0x00,
        .base_hi       = (uint8_t)((tss_base >> 24) & 0xFF),
        .base_upper    = (uint32_t)(tss_base >> 32),
        .reserved      = 0,
    };

    /* Load GDT */
    gdtr.limit = sizeof(gdt) - 1;
    gdtr.base  = (uint64_t)&gdt;
    gdt_flush(&gdtr);

    serial_puts("ARCH: GDT loaded\n");
}

/* ------------------------------------------------------------------ */
/*  gdt_set_tss_rsp0 — update TSS.rsp0 for user→kernel transitions   */
/* ------------------------------------------------------------------ */

void gdt_set_tss_rsp0(uint64_t rsp0) {
    tss.rsp0 = rsp0;
}
