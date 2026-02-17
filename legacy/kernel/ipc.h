#ifndef IPC_H
#define IPC_H

#include <stdint.h>

#define MAX_IPC_ENDPOINTS   16
#define IPC_MSG_QUEUE_DEPTH  4
#define IPC_MSG_MAX_SIZE   128

struct ipc_message {
    uint32_t sender_tid;
    uint32_t size;
    uint8_t  data[IPC_MSG_MAX_SIZE];
};

struct ipc_endpoint {
    uint32_t port;
    uint32_t owner_tid;
    struct ipc_message queue[IPC_MSG_QUEUE_DEPTH];
    uint32_t head;
    uint32_t tail;
    uint32_t count;
    struct thread *blocked_receiver;
};

void     ipc_init(void);
uint32_t ipc_create_port(void);
int      ipc_send(uint32_t port, const void *buf, uint32_t size);
int      ipc_recv(uint32_t port, void *buf, uint32_t *sender_tid_out);

#endif
