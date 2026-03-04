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

global main.sysThreadSpawn
main.sysThreadSpawn:
    mov  eax, 1
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

global main.sysVmMap
main.sysVmMap:
    mov  eax, 4
    int  0x80
    ret

global main.sysVmUnmap
main.sysVmUnmap:
    mov  eax, 5
    int  0x80
    ret

global main.sysTimeNow
main.sysTimeNow:
    mov  eax, 10
    int  0x80
    ret

global main.sysSpawnEntry
main.sysSpawnEntry:
    lea  rax, [rel gostd_spawn_entry]
    ret

gostd_spawn_entry:
    lea  rdi, [rel msg_spawn_child_ok]
    mov  esi, msg_spawn_child_ok_end - msg_spawn_child_ok
    xor  eax, eax
    int  0x80

    mov  eax, 2
    int  0x80
.hang:
    hlt
    jmp  .hang

section .rodata
msg_spawn_child_ok: db "GOSTD: spawn child ok", 10
msg_spawn_child_ok_end:
