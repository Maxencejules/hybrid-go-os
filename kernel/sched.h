#ifndef SCHED_H
#define SCHED_H

#include <stdint.h>

#define MAX_THREADS      8
#define THREAD_STACK_SIZE 16384

enum thread_state {
    THREAD_READY,
    THREAD_RUNNING,
    THREAD_DEAD
};

struct thread {
    uint64_t rsp;
    uint8_t *stack_base;
    uint32_t stack_size;
    enum thread_state state;
    struct thread *next;
    uint32_t tid;
    uint64_t cr3;
    uint64_t kernel_stack_top;
};

extern struct thread *current_thread;

void           sched_init(void);
struct thread *thread_create(void (*func)(void));
struct thread *thread_create_user(uint64_t cr3, uint64_t entry, uint64_t user_stack);
void           schedule(void);
void           thread_exit(void);

/* Spinlock */
struct spinlock {
    volatile uint32_t locked;
};

void spin_lock(struct spinlock *lk);
void spin_unlock(struct spinlock *lk);

#endif
