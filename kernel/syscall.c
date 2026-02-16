#include <stdint.h>
#include "syscall.h"
#include "serial.h"
#include "sched.h"
#include "ipc.h"
#include "shm.h"
#include "service_registry.h"
#include "virtio_blk.h"
#include "process.h"

extern volatile uint64_t tick_count;

void syscall_handler(struct interrupt_frame *frame) {
    uint64_t num  = frame->rax;
    uint64_t arg1 = frame->rdi;
    uint64_t arg2 = frame->rsi;
    uint64_t arg3 = frame->rdx;

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

    case SYS_SHM_CREATE:
        frame->rax = (uint64_t)shm_create((uint32_t)arg1);
        break;

    case SYS_SHM_MAP:
        frame->rax = shm_map((uint32_t)arg1, arg2);
        break;

    case SYS_IPC_SEND:
        frame->rax = (uint64_t)(int64_t)ipc_send((uint32_t)arg1, (const void *)arg2, (uint32_t)arg3);
        break;

    case SYS_IPC_RECV:
        frame->rax = (uint64_t)(int64_t)ipc_recv((uint32_t)arg1, (void *)arg2, (uint32_t *)arg3);
        break;

    case SYS_IPC_CREATE_PORT:
        frame->rax = (uint64_t)ipc_create_port();
        break;

    case SYS_SERVICE_REGISTER:
        frame->rax = (uint64_t)(int64_t)service_register((const char *)arg1, (uint32_t)arg2);
        break;

    case SYS_SERVICE_LOOKUP:
        frame->rax = (uint64_t)service_lookup((const char *)arg1);
        break;

    case SYS_BLK_READ: {
        uint64_t sector = arg1;
        void *buf = (void *)arg2;
        uint32_t count = (uint32_t)arg3;
        if ((uint64_t)buf >= 0x8000000000000000ULL) {
            frame->rax = (uint64_t)-1;
            break;
        }
        frame->rax = (uint64_t)(int64_t)virtio_blk_read(sector, buf, count);
        break;
    }

    case SYS_BLK_WRITE: {
        uint64_t sector = arg1;
        const void *buf = (const void *)arg2;
        uint32_t count = (uint32_t)arg3;
        if ((uint64_t)buf >= 0x8000000000000000ULL) {
            frame->rax = (uint64_t)-1;
            break;
        }
        frame->rax = (uint64_t)(int64_t)virtio_blk_write(sector, buf, count);
        break;
    }

    case SYS_PROCESS_SPAWN: {
        uint64_t bin_ptr = arg1;
        uint64_t bin_size = arg2;
        if (bin_ptr >= 0x8000000000000000ULL ||
            bin_ptr + bin_size >= 0x8000000000000000ULL ||
            bin_size == 0 || bin_size > 64 * 1024) {
            frame->rax = (uint64_t)-1;
            break;
        }
        struct thread *t = process_create((const void *)bin_ptr, bin_size);
        frame->rax = t ? (uint64_t)t->tid : (uint64_t)-1;
        break;
    }

    default:
        frame->rax = (uint64_t)-1;
        break;
    }
}
