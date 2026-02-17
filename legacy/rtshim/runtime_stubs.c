/*
 * rtshim/runtime_stubs.c — Minimal stubs for gccgo runtime symbols
 *
 * gccgo-compiled code may reference Go runtime helpers even for trivial
 * functions. We provide no-op or halt stubs here. Add more as the linker
 * demands them.
 */

#include <stdint.h>

/* Called on runtime errors (bounds checks, nil derefs, etc.) */
void __go_runtime_error(int32_t code) {
    (void)code;
    for (;;)
        __asm__ volatile ("cli; hlt");
}

/* GC root registration — no-op since we have no garbage collector */
void __go_register_gc_roots(void *roots) {
    (void)roots;
}

/* Nil pointer check — no-op (we rely on page fault handler) */
void __go_nil_check(void *p) {
    (void)p;
}
