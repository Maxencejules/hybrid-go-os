#include "syscall.h"

void main(void) {
    sys_debug_write("USER: hello\n", 12);
    sys_time_now();
    sys_debug_write("SYSCALL: ok\n", 12);

    for (;;)
        sys_yield();
}
