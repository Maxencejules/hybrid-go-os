#include "syscall.h"

void main(void) {
    sys_debug_write("APP: hello world\n", 17);
    for (;;) sys_yield();
}
