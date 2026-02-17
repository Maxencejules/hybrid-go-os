#include "syscall.h"

void main(void) {
    volatile char *bad = (volatile char *)0xDEAD0000;
    char x = *bad;
    (void)x;
}
