#include "syscall.h"

void main(void) {
    /* Create our own port for replies */
    uint32_t my_port = sys_ipc_create_port();

    /* Retry until pong service is registered */
    uint32_t pong_port = 0;
    while (pong_port == 0) {
        pong_port = sys_service_lookup("pong");
        if (pong_port == 0)
            sys_yield();
    }

    /* Build message: "PING" + our port number for reply */
    char msg[8];
    msg[0] = 'P'; msg[1] = 'I'; msg[2] = 'N'; msg[3] = 'G';
    *(uint32_t *)(msg + 4) = my_port;

    sys_ipc_send(pong_port, msg, 8);

    /* Wait for PONG reply */
    char reply[128];
    uint32_t sender;
    sys_ipc_recv(my_port, reply, &sender);

    if (reply[0] == 'P' && reply[1] == 'O' && reply[2] == 'N' && reply[3] == 'G') {
        sys_debug_write("PING: ok\n", 9);
    }

    for (;;)
        sys_yield();
}
