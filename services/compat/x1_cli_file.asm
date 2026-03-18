bits 64
default rel

%define SYS_DEBUG_WRITE 0
%define SYS_THREAD_EXIT 2
%define SYS_OPEN 18
%define SYS_READ 19
%define SYS_CLOSE 21
%define SYS_POLL 23
%define SYS_QEMU_EXIT 98

%define OPEN_RDONLY 0
%define POLLIN 1

global _start

section .text
_start:
    lea  rdi, [rel msg_start]
    mov  esi, msg_start_end - msg_start
    xor  eax, eax
    int  0x80

    lea  rdi, [rel path_file]
    mov  esi, OPEN_RDONLY
    xor  edx, edx
    mov  eax, SYS_OPEN
    int  0x80
    cmp  rax, -1
    je   fail_open
    mov  [file_fd], rax

    mov  eax, [file_fd]
    mov  [pollfds + 0], eax
    mov  word [pollfds + 4], POLLIN
    mov  word [pollfds + 6], 0

    lea  rdi, [rel pollfds]
    mov  esi, 1
    xor  edx, edx
    mov  eax, SYS_POLL
    int  0x80
    cmp  rax, 1
    jne  fail_poll
    cmp  word [pollfds + 6], POLLIN
    jne  fail_poll

    mov  rdi, [file_fd]
    lea  rsi, [rel read_buf]
    mov  edx, expected_data_end - expected_data
    mov  eax, SYS_READ
    int  0x80
    cmp  rax, expected_data_end - expected_data
    jne  fail_read

    cld
    lea  rsi, [rel read_buf]
    lea  rdi, [rel expected_data]
    mov  ecx, expected_data_end - expected_data
    repe cmpsb
    jne  fail_read

    mov  rdi, [file_fd]
    mov  eax, SYS_CLOSE
    int  0x80
    cmp  rax, -1
    je   fail_close

    lea  rdi, [rel msg_ok]
    mov  esi, msg_ok_end - msg_ok
    xor  eax, eax
    int  0x80

    mov  eax, SYS_THREAD_EXIT
    int  0x80

hang:
    hlt
    jmp  hang

fail_open:
    lea  rdi, [rel msg_fail_open]
    mov  esi, msg_fail_open_end - msg_fail_open
    xor  eax, eax
    int  0x80
    jmp  fail_exit

fail_poll:
    lea  rdi, [rel msg_fail_poll]
    mov  esi, msg_fail_poll_end - msg_fail_poll
    xor  eax, eax
    int  0x80
    jmp  fail_exit

fail_read:
    lea  rdi, [rel msg_fail_read]
    mov  esi, msg_fail_read_end - msg_fail_read
    xor  eax, eax
    int  0x80
    jmp  fail_exit

fail_close:
    lea  rdi, [rel msg_fail_close]
    mov  esi, msg_fail_close_end - msg_fail_close
    xor  eax, eax
    int  0x80
    jmp  fail_exit

fail_exit:
    lea  rdi, [rel msg_fail]
    mov  esi, msg_fail_end - msg_fail
    xor  eax, eax
    int  0x80

    mov  edi, 0x33
    mov  eax, SYS_QEMU_EXIT
    int  0x80
    jmp  hang

section .data
msg_start:      db "X1CLI: start", 10
msg_start_end:
msg_ok:         db "X1CLI: file ok", 10
msg_ok_end:
msg_fail_open:  db "X1CLI: fail open", 10
msg_fail_open_end:
msg_fail_poll:  db "X1CLI: fail poll", 10
msg_fail_poll_end:
msg_fail_read:  db "X1CLI: fail read", 10
msg_fail_read_end:
msg_fail_close: db "X1CLI: fail close", 10
msg_fail_close_end:
msg_fail:       db "X1CLI: fail", 10
msg_fail_end:
path_file:      db "/compat/hello.txt", 0
expected_data:  db "compat v1 hello", 10
expected_data_end:

section .bss
file_fd:        resq 1
pollfds:        resb 8
read_buf:       resb 32
