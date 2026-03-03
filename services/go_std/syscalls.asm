; Rugo x86_64 user-space syscall wrappers for the G2 std-port spike target.
; TinyGo C ABI (System V AMD64): rdi, rsi, rdx, rcx, r8, r9.
; Rugo syscall ABI: rax=nr, rdi=a1, rsi=a2, rdx=a3; int 0x80.

bits 64
default rel

section .text

global main.sysDebugWrite
main.sysDebugWrite:
    xor  eax, eax
    int  0x80
    ret

global main.sysThreadExit
main.sysThreadExit:
    mov  eax, 2
    int  0x80
    ret

global main.sysYield
main.sysYield:
    mov  eax, 3
    int  0x80
    ret

global main.sysTimeNow
main.sysTimeNow:
    mov  eax, 10
    int  0x80
    ret
