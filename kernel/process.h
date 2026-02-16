#ifndef PROCESS_H
#define PROCESS_H

#include <stdint.h>
#include "sched.h"

#define USER_CODE_BASE  0x400000
#define USER_STACK_BASE 0x7FF000
#define USER_STACK_SIZE 4096

struct thread *process_create(const void *binary, uint64_t size);

#endif
