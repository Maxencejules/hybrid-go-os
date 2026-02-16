#ifndef SYSCALL_H
#define SYSCALL_H

#include <stdint.h>
#include "../arch/x86_64/idt.h"

#define SYS_DEBUG_WRITE     0
#define SYS_THREAD_SPAWN    1
#define SYS_THREAD_EXIT     2
#define SYS_YIELD           3
#define SYS_VM_MAP          4
#define SYS_VM_UNMAP        5
#define SYS_SHM_CREATE      6
#define SYS_SHM_MAP         7
#define SYS_IPC_SEND        8
#define SYS_IPC_RECV        9
#define SYS_TIME_NOW       10
#define SYS_IPC_CREATE_PORT 11
#define SYS_SERVICE_REGISTER 12
#define SYS_SERVICE_LOOKUP  13
#define SYS_BLK_READ       14
#define SYS_BLK_WRITE      15
#define SYS_PROCESS_SPAWN  16
#define SYS_NET_SEND       17
#define SYS_NET_RECV       18
#define SYS_NET_GET_MAC    19

void syscall_handler(struct interrupt_frame *frame);

#endif
