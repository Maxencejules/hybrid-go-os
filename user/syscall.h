#ifndef USER_SYSCALL_H
#define USER_SYSCALL_H

typedef unsigned long long uint64_t;
typedef long long int64_t;

#define SYS_DEBUG_WRITE 0
#define SYS_THREAD_EXIT 2
#define SYS_YIELD       3
#define SYS_TIME_NOW    10

static inline int64_t syscall0(uint64_t num) {
    int64_t ret;
    __asm__ volatile (
        "int $0x80"
        : "=a"(ret)
        : "a"(num)
        : "memory", "rcx", "r11"
    );
    return ret;
}

static inline int64_t syscall2(uint64_t num, uint64_t a1, uint64_t a2) {
    int64_t ret;
    __asm__ volatile (
        "int $0x80"
        : "=a"(ret)
        : "a"(num), "D"(a1), "S"(a2)
        : "memory", "rcx", "r11"
    );
    return ret;
}

static inline int64_t sys_debug_write(const char *buf, uint64_t len) {
    return syscall2(SYS_DEBUG_WRITE, (uint64_t)buf, len);
}

static inline void sys_thread_exit(void) {
    syscall0(SYS_THREAD_EXIT);
}

static inline void sys_yield(void) {
    syscall0(SYS_YIELD);
}

static inline int64_t sys_time_now(void) {
    return syscall0(SYS_TIME_NOW);
}

#endif
