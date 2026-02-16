#include <stdint.h>
#include <stddef.h>
#include "sched.h"
#include "serial.h"

/* Static thread stacks (slot 0 unused — idle thread uses boot stack) */
static uint8_t stacks[MAX_THREADS][THREAD_STACK_SIZE]
    __attribute__((aligned(16)));

static struct thread threads[MAX_THREADS];
static uint32_t next_tid = 0;

struct thread *current_thread = NULL;

/* Assembly helpers (context.asm) */
extern void context_switch(uint64_t *old_rsp, uint64_t new_rsp);
extern void thread_entry_trampoline(void);

void sched_init(void) {
    threads[0] = (struct thread){
        .rsp        = 0,
        .stack_base = NULL,
        .stack_size = 0,
        .state      = THREAD_RUNNING,
        .next       = &threads[0],
        .tid        = 0
    };
    current_thread = &threads[0];
    next_tid = 1;

    serial_puts("SCHED: initialized\n");
}

struct thread *thread_create(void (*func)(void)) {
    if (next_tid >= MAX_THREADS)
        return NULL;

    uint32_t tid = next_tid++;
    struct thread *t = &threads[tid];

    t->tid        = tid;
    t->stack_base = stacks[tid];
    t->stack_size = THREAD_STACK_SIZE;
    t->state      = THREAD_READY;

    /* Build initial stack frame for context_switch */
    uint64_t *sp = (uint64_t *)(t->stack_base + t->stack_size);

    *(--sp) = (uint64_t)thread_exit;              /* return from func */
    *(--sp) = (uint64_t)func;                     /* return from trampoline */
    *(--sp) = (uint64_t)thread_entry_trampoline;  /* return from context_switch */
    *(--sp) = 0;  /* r15 */
    *(--sp) = 0;  /* r14 */
    *(--sp) = 0;  /* r13 */
    *(--sp) = 0;  /* r12 */
    *(--sp) = 0;  /* rbx */
    *(--sp) = 0;  /* rbp */

    t->rsp = (uint64_t)sp;

    /* Insert into circular list after current */
    t->next = current_thread->next;
    current_thread->next = t;

    serial_puts("SCHED: created thread ");
    serial_put_hex(tid);
    serial_putc('\n');

    return t;
}

void schedule(void) {
    struct thread *old = current_thread;
    struct thread *next = old->next;

    /* Find next READY thread */
    while (next->state == THREAD_DEAD && next != old)
        next = next->next;

    if (next == old || next->state != THREAD_READY)
        return;

    old->state = (old->state == THREAD_RUNNING) ? THREAD_READY : old->state;
    next->state = THREAD_RUNNING;
    current_thread = next;

    context_switch(&old->rsp, next->rsp);
}

void thread_exit(void) {
    current_thread->state = THREAD_DEAD;
    schedule();

    for (;;)
        __asm__ volatile ("cli; hlt");
}

/* Spinlock */
void spin_lock(struct spinlock *lk) {
    __asm__ volatile ("cli");
    while (__sync_lock_test_and_set(&lk->locked, 1))
        __asm__ volatile ("pause");
}

void spin_unlock(struct spinlock *lk) {
    __sync_lock_release(&lk->locked);
    __asm__ volatile ("sti");
}
