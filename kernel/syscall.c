#include <stdint.h>
#include "syscall.h"
#include "serial.h"
#include "sched.h"

extern volatile uint64_t tick_count;

void syscall_handler(struct interrupt_frame *frame) {
    uint64_t num  = frame->rax;
    uint64_t arg1 = frame->rdi;
    uint64_t arg2 = frame->rsi;

    switch (num) {
    case SYS_DEBUG_WRITE: {
        const char *buf = (const char *)arg1;
        uint64_t len = arg2;

        /* Basic user-pointer validation */
        if ((uint64_t)buf >= 0x8000000000000000ULL) {
            frame->rax = (uint64_t)-1;
            break;
        }

        for (uint64_t i = 0; i < len; i++)
            serial_putc(buf[i]);

        frame->rax = (uint64_t)len;
        break;
    }
    case SYS_THREAD_EXIT:
        thread_exit();
        break;

    case SYS_YIELD:
        schedule();
        frame->rax = 0;
        break;

    case SYS_TIME_NOW:
        frame->rax = tick_count;
        break;

    default:
        frame->rax = (uint64_t)-1;
        break;
    }
}
