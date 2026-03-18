bits 64
default rel

%define SYS_DEBUG_WRITE 0
%define SYS_THREAD_SPAWN 1
%define SYS_THREAD_EXIT 2
%define SYS_WAIT 22
%define SYS_SOCKET_OPEN 31
%define SYS_SOCKET_BIND 32
%define SYS_SOCKET_LISTEN 33
%define SYS_SOCKET_CONNECT 34
%define SYS_SOCKET_ACCEPT 35
%define SYS_SOCKET_SEND 36
%define SYS_SOCKET_RECV 37
%define SYS_SOCKET_CLOSE 38
%define SYS_NET_IF_CONFIG 39
%define SYS_NET_ROUTE_ADD 40
%define SYS_FORK_DEFERRED 43
%define SYS_CLONE_DEFERRED 44
%define SYS_EPOLL_DEFERRED 45
%define SYS_QEMU_EXIT 98

%define NET_AF_INET6 10
%define SOCKET_STREAM 1

global _start

section .text
_start:
    lea  rdi, [rel msg_start]
    mov  esi, msg_start_end - msg_start
    xor  eax, eax
    int  0x80

    lea  rdi, [rel child_entry]
    mov  eax, SYS_THREAD_SPAWN
    int  0x80
    cmp  rax, -1
    je   fail
    mov  [child_tid], rax

    mov  rdi, -1
    lea  rsi, [rel wait_status]
    xor  edx, edx
    mov  eax, SYS_WAIT
    int  0x80
    cmp  rax, -1
    je   fail
    cmp  rax, qword [child_tid]
    jne  fail
    cmp  qword [wait_status], 0
    jne  fail

    lea  rdi, [rel msg_wait_ok]
    mov  esi, msg_wait_ok_end - msg_wait_ok
    xor  eax, eax
    int  0x80

    xor  edi, edi
    lea  rsi, [rel loopback_cfg]
    mov  edx, 32
    mov  eax, SYS_NET_IF_CONFIG
    int  0x80
    cmp  rax, -1
    je   fail

    xor  edi, edi
    lea  rsi, [rel loopback_cfg]
    mov  edx, 32
    mov  eax, SYS_NET_ROUTE_ADD
    int  0x80
    cmp  rax, -1
    je   fail

    mov  edi, NET_AF_INET6
    mov  esi, SOCKET_STREAM
    mov  eax, SYS_SOCKET_OPEN
    int  0x80
    cmp  rax, -1
    je   fail
    mov  [server_socket], rax

    mov  rdi, [server_socket]
    lea  rsi, [rel listen_addr]
    mov  edx, 32
    mov  eax, SYS_SOCKET_BIND
    int  0x80
    cmp  rax, -1
    je   fail

    mov  rdi, [server_socket]
    mov  esi, 1
    mov  eax, SYS_SOCKET_LISTEN
    int  0x80
    cmp  rax, -1
    je   fail

    mov  edi, NET_AF_INET6
    mov  esi, SOCKET_STREAM
    mov  eax, SYS_SOCKET_OPEN
    int  0x80
    cmp  rax, -1
    je   fail
    mov  [client_socket], rax

    mov  rdi, [client_socket]
    lea  rsi, [rel listen_addr]
    mov  edx, 32
    mov  eax, SYS_SOCKET_CONNECT
    int  0x80
    cmp  rax, -1
    je   fail

    mov  qword [peer_len], 32
    mov  rdi, [server_socket]
    lea  rsi, [rel peer_addr]
    lea  rdx, [rel peer_len]
    mov  eax, SYS_SOCKET_ACCEPT
    int  0x80
    cmp  rax, -1
    je   fail
    mov  [accepted_socket], rax

    mov  rdi, [client_socket]
    lea  rsi, [rel payload_ping]
    mov  edx, payload_ping_end - payload_ping
    mov  eax, SYS_SOCKET_SEND
    int  0x80
    cmp  rax, payload_ping_end - payload_ping
    jne  fail

    mov  rdi, [accepted_socket]
    lea  rsi, [rel recv_buf]
    mov  edx, 16
    mov  eax, SYS_SOCKET_RECV
    int  0x80
    cmp  rax, payload_ping_end - payload_ping
    jne  fail

    cld
    lea  rsi, [rel recv_buf]
    lea  rdi, [rel payload_ping]
    mov  ecx, payload_ping_end - payload_ping
    repe cmpsb
    jne  fail

    mov  rdi, [accepted_socket]
    lea  rsi, [rel payload_reply]
    mov  edx, payload_reply_end - payload_reply
    mov  eax, SYS_SOCKET_SEND
    int  0x80
    cmp  rax, payload_reply_end - payload_reply
    jne  fail

    mov  rdi, [client_socket]
    lea  rsi, [rel recv_buf]
    mov  edx, 16
    mov  eax, SYS_SOCKET_RECV
    int  0x80
    cmp  rax, payload_reply_end - payload_reply
    jne  fail

    cld
    lea  rsi, [rel recv_buf]
    lea  rdi, [rel payload_reply]
    mov  ecx, payload_reply_end - payload_reply
    repe cmpsb
    jne  fail

    mov  rdi, [accepted_socket]
    mov  eax, SYS_SOCKET_CLOSE
    int  0x80
    cmp  rax, -1
    je   fail

    mov  rdi, [client_socket]
    mov  eax, SYS_SOCKET_CLOSE
    int  0x80
    cmp  rax, -1
    je   fail

    mov  rdi, [server_socket]
    mov  eax, SYS_SOCKET_CLOSE
    int  0x80
    cmp  rax, -1
    je   fail

    lea  rdi, [rel msg_sock_ok]
    mov  esi, msg_sock_ok_end - msg_sock_ok
    xor  eax, eax
    int  0x80

    mov  eax, SYS_FORK_DEFERRED
    int  0x80
    cmp  rax, -1
    jne  fail

    mov  eax, SYS_CLONE_DEFERRED
    int  0x80
    cmp  rax, -1
    jne  fail

    mov  eax, SYS_EPOLL_DEFERRED
    int  0x80
    cmp  rax, -1
    jne  fail

    lea  rdi, [rel msg_defer_ok]
    mov  esi, msg_defer_ok_end - msg_defer_ok
    xor  eax, eax
    int  0x80

    mov  eax, SYS_THREAD_EXIT
    int  0x80

hang:
    hlt
    jmp  hang

child_entry:
    lea  rdi, [rel msg_child_ok]
    mov  esi, msg_child_ok_end - msg_child_ok
    xor  eax, eax
    int  0x80
    mov  eax, SYS_THREAD_EXIT
    int  0x80
    jmp  hang

fail:
    lea  rdi, [rel msg_fail]
    mov  esi, msg_fail_end - msg_fail
    xor  eax, eax
    int  0x80

    mov  edi, 0x33
    mov  eax, SYS_QEMU_EXIT
    int  0x80
    jmp  hang

section .data
msg_start:       db "X1PROC: start", 10
msg_start_end:
msg_child_ok:    db "X1PROC: child ok", 10
msg_child_ok_end:
msg_wait_ok:     db "X1PROC: wait ok", 10
msg_wait_ok_end:
msg_sock_ok:     db "X1SOCK: ok", 10
msg_sock_ok_end:
msg_defer_ok:    db "X1DEFER: ok", 10
msg_defer_ok_end:
msg_fail:        db "X1PROC: fail", 10
msg_fail_end:
payload_ping:    db "ping"
payload_ping_end:
payload_reply:   db "OK"
payload_reply_end:

loopback_cfg:
    dq NET_AF_INET6
    dq 128
    db 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1

listen_addr:
    dq NET_AF_INET6
    dq 5050
    db 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1

section .bss
child_tid:       resq 1
wait_status:     resq 1
server_socket:   resq 1
client_socket:   resq 1
accepted_socket: resq 1
peer_len:        resq 1
peer_addr:       resb 32
recv_buf:        resb 32
