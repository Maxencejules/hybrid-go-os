#include "syscall.h"

void main(void) {
    /* Create port and register as "pong" */
    uint32_t my_port = sys_ipc_create_port();
    sys_service_register("pong", my_port);

    /* Wait for PING message */
    char msg[128];
    uint32_t sender;
    sys_ipc_recv(my_port, msg, &sender);

    /* Verify PING and extract reply port */
    if (msg[0] == 'P' && msg[1] == 'I' && msg[2] == 'N' && msg[3] == 'G') {
        uint32_t reply_port = *(uint32_t *)(msg + 4);

        /* Send PONG reply */
        char reply[4];
        reply[0] = 'P'; reply[1] = 'O'; reply[2] = 'N'; reply[3] = 'G';
        sys_ipc_send(reply_port, reply, 4);

        sys_debug_write("PONG: ok\n", 9);
    }

    for (;;)
        sys_yield();
}
