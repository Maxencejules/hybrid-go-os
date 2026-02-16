#ifndef USER_SYSCALL_H
#define USER_SYSCALL_H

typedef unsigned long long uint64_t;
typedef long long int64_t;
typedef unsigned int uint32_t;
typedef unsigned short uint16_t;
typedef unsigned char uint8_t;

#define SYS_DEBUG_WRITE     0
#define SYS_THREAD_EXIT     2
#define SYS_YIELD           3
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

static inline int64_t syscall3(uint64_t num, uint64_t a1, uint64_t a2, uint64_t a3) {
    int64_t ret;
    register uint64_t r_a3 __asm__("rdx") = a3;
    __asm__ volatile (
        "int $0x80"
        : "=a"(ret)
        : "a"(num), "D"(a1), "S"(a2), "r"(r_a3)
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

static inline uint32_t sys_ipc_create_port(void) {
    return (uint32_t)syscall0(SYS_IPC_CREATE_PORT);
}

static inline int64_t sys_ipc_send(uint32_t port, const void *buf, uint32_t size) {
    return syscall3(SYS_IPC_SEND, (uint64_t)port, (uint64_t)buf, (uint64_t)size);
}

static inline int64_t sys_ipc_recv(uint32_t port, void *buf, uint32_t *sender_tid) {
    return syscall3(SYS_IPC_RECV, (uint64_t)port, (uint64_t)buf, (uint64_t)sender_tid);
}

static inline uint32_t sys_shm_create(uint32_t size) {
    return (uint32_t)syscall2(SYS_SHM_CREATE, (uint64_t)size, 0);
}

static inline uint64_t sys_shm_map(uint32_t handle, uint64_t vaddr_hint) {
    return (uint64_t)syscall2(SYS_SHM_MAP, (uint64_t)handle, vaddr_hint);
}

static inline int64_t sys_service_register(const char *name, uint32_t port) {
    return syscall2(SYS_SERVICE_REGISTER, (uint64_t)name, (uint64_t)port);
}

static inline uint32_t sys_service_lookup(const char *name) {
    return (uint32_t)syscall2(SYS_SERVICE_LOOKUP, (uint64_t)name, 0);
}

static inline int64_t sys_blk_read(uint64_t sector, void *buf, uint32_t count) {
    return syscall3(SYS_BLK_READ, sector, (uint64_t)buf, (uint64_t)count);
}

static inline int64_t sys_blk_write(uint64_t sector, const void *buf, uint32_t count) {
    return syscall3(SYS_BLK_WRITE, sector, (uint64_t)buf, (uint64_t)count);
}

static inline int64_t sys_process_spawn(const void *binary, uint64_t size) {
    return syscall2(SYS_PROCESS_SPAWN, (uint64_t)binary, size);
}

static inline int64_t sys_net_send(const void *frame, uint32_t len) {
    return syscall2(SYS_NET_SEND, (uint64_t)frame, (uint64_t)len);
}

static inline int64_t sys_net_recv(void *frame, uint32_t max_len) {
    return syscall2(SYS_NET_RECV, (uint64_t)frame, (uint64_t)max_len);
}

static inline int64_t sys_net_get_mac(uint8_t *mac) {
    return syscall2(SYS_NET_GET_MAC, (uint64_t)mac, 0);
}

#endif
