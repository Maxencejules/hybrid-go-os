#include <stdint.h>
#include <stddef.h>
#include "ipc.h"
#include "sched.h"
#include "serial.h"
#include "string.h"

static struct ipc_endpoint endpoints[MAX_IPC_ENDPOINTS];
static uint32_t next_port = 1;

void ipc_init(void) {
    for (int i = 0; i < MAX_IPC_ENDPOINTS; i++)
        endpoints[i].port = 0;
    serial_puts("IPC: initialized\n");
}

static struct ipc_endpoint *find_endpoint(uint32_t port) {
    for (int i = 0; i < MAX_IPC_ENDPOINTS; i++) {
        if (endpoints[i].port == port)
            return &endpoints[i];
    }
    return NULL;
}

uint32_t ipc_create_port(void) {
    for (int i = 0; i < MAX_IPC_ENDPOINTS; i++) {
        if (endpoints[i].port == 0) {
            uint32_t port = next_port++;
            endpoints[i].port = port;
            endpoints[i].owner_tid = current_thread->tid;
            endpoints[i].head = 0;
            endpoints[i].tail = 0;
            endpoints[i].count = 0;
            endpoints[i].blocked_receiver = NULL;
            return port;
        }
    }
    return 0;
}

int ipc_send(uint32_t port, const void *buf, uint32_t size) {
    if (size > IPC_MSG_MAX_SIZE)
        return -1;
    if ((uint64_t)buf >= 0x8000000000000000ULL)
        return -1;

    struct ipc_endpoint *ep = find_endpoint(port);
    if (!ep)
        return -1;

    __asm__ volatile ("cli");

    if (ep->count >= IPC_MSG_QUEUE_DEPTH) {
        __asm__ volatile ("sti");
        return -1;
    }

    struct ipc_message *slot = &ep->queue[ep->tail];
    slot->sender_tid = current_thread->tid;
    slot->size = size;
    memcpy(slot->data, buf, size);
    ep->tail = (ep->tail + 1) % IPC_MSG_QUEUE_DEPTH;
    ep->count++;

    /* Wake blocked receiver */
    if (ep->blocked_receiver && ep->blocked_receiver->state == THREAD_BLOCKED) {
        ep->blocked_receiver->state = THREAD_READY;
        ep->blocked_receiver = NULL;
    }

    __asm__ volatile ("sti");
    return 0;
}

int ipc_recv(uint32_t port, void *buf, uint32_t *sender_tid_out) {
    if ((uint64_t)buf >= 0x8000000000000000ULL)
        return -1;

    struct ipc_endpoint *ep = find_endpoint(port);
    if (!ep || ep->owner_tid != current_thread->tid)
        return -1;

    __asm__ volatile ("cli");

    /* Block until message available */
    while (ep->count == 0) {
        ep->blocked_receiver = current_thread;
        current_thread->state = THREAD_BLOCKED;
        schedule();
        __asm__ volatile ("cli");
    }

    /* Dequeue */
    struct ipc_message *msg = &ep->queue[ep->head];
    uint32_t size = msg->size;
    memcpy(buf, msg->data, size);
    if (sender_tid_out && (uint64_t)sender_tid_out < 0x8000000000000000ULL)
        *sender_tid_out = msg->sender_tid;
    ep->head = (ep->head + 1) % IPC_MSG_QUEUE_DEPTH;
    ep->count--;

    __asm__ volatile ("sti");
    return (int)size;
}
