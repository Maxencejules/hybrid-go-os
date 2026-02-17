/*
 * rtshim/bridge.c — C-to-Go bridge for kernel entry
 *
 * Calls the gccgo-compiled GoKmain() and verifies the return value.
 * The __asm__ attribute tells GCC to use the exact gccgo symbol name.
 */

#include "../kernel/serial.h"

/* gccgo symbol: package "kernelgo", function "GoKmain" */
extern long GoKmain(void) __asm__("kernelgo.GoKmain");

void go_kmain(void) {
    long result = GoKmain();
    if (result == 42) {
        serial_puts("GO: kmain ok\n");
    } else {
        serial_puts("GO: kmain FAIL\n");
    }
}
