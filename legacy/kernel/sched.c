#include <stdint.h>
#include <stddef.h>
#include "sched.h"
#include "serial.h"
#include "vmm.h"
#include "../arch/x86_64/gdt.h"

/* Static thread stacks (slot 0 unused — idle thread uses boot stack) */
static uint8_t stacks[MAX_THREADS][THREAD_STACK_SIZE]
    __attribute__((aligned(16)));

static struct thread threads[MAX_THREADS];
static uint32_t next_tid = 0;

struct thread *current_thread = NULL;

/* Assembly helpers (context.asm) */
extern void context_switch(uint64_t *old_rsp, uint64_t new_rsp);
extern void thread_entry_trampoline(void);
extern void user_mode_trampoline(void);

static inline uint64_t read_cr3(void) {
    uint64_t val;
    __asm__ volatile ("mov %%cr3, %0" : "=r"(val));
    return val;
}

static inline void write_cr3(uint64_t val) {
    __asm__ volatile ("mov %0, %%cr3" :: "r"(val) : "memory");
}

void sched_init(void) {
    threads[0] = (struct thread){
        .rsp        = 0,
        .stack_base = NULL,
        .stack_size = 0,
        .state      = THREAD_RUNNING,
        .next       = &threads[0],
        .tid        = 0,
        .cr3        = 0,
        .kernel_stack_top = 0
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
    t->cr3        = 0;
    t->kernel_stack_top = 0;

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

struct thread *thread_create_user(uint64_t cr3, uint64_t entry, uint64_t user_stack) {
    if (next_tid >= MAX_THREADS)
        return NULL;

    uint32_t tid = next_tid++;
    struct thread *t = &threads[tid];

    t->tid        = tid;
    t->stack_base = stacks[tid];
    t->stack_size = THREAD_STACK_SIZE;
    t->state      = THREAD_READY;
    t->cr3        = cr3;
    t->kernel_stack_top = (uint64_t)(t->stack_base + t->stack_size);

    /* Build initial stack frame for context_switch → user_mode_trampoline */
    uint64_t *sp = (uint64_t *)(t->stack_base + t->stack_size);

    *(--sp) = user_stack;                          /* for trampoline: user RSP */
    *(--sp) = entry;                               /* for trampoline: user RIP */
    *(--sp) = (uint64_t)user_mode_trampoline;      /* return from context_switch */
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

    serial_puts("SCHED: created user thread ");
    serial_put_hex(tid);
    serial_putc('\n');

    return t;
}

void schedule(void) {
    struct thread *old = current_thread;
    struct thread *next = old->next;

    /* Find next READY thread (skip DEAD and BLOCKED) */
    while ((next->state == THREAD_DEAD || next->state == THREAD_BLOCKED) && next != old)
        next = next->next;

    if (next == old || next->state != THREAD_READY)
        return;

    old->state = (old->state == THREAD_RUNNING) ? THREAD_READY : old->state;
    next->state = THREAD_RUNNING;
    current_thread = next;

    /* Switch CR3 if different */
    uint64_t next_cr3 = next->cr3 ? next->cr3 : kernel_cr3;
    uint64_t cur_cr3 = read_cr3();
    if (next_cr3 != cur_cr3)
        write_cr3(next_cr3);

    /* Update TSS.rsp0 for user threads */
    if (next->kernel_stack_top)
        gdt_set_tss_rsp0(next->kernel_stack_top);

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
