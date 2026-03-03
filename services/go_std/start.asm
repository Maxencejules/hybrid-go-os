; Rugo x86_64 user-space startup + syscall wrapper + runtime stubs
; for the G2 std-port spike target.

bits 64
default rel

; ---------- Entry point ----------
section .text._start
global _start
extern main
_start:
    call main
    hlt
    jmp _start

; ---------- Syscall wrappers ----------
; TinyGo C ABI (System V AMD64): rdi, rsi, rdx, rcx, r8, r9.
; Rugo syscall: rax=nr, rdi=a1, rsi=a2, rdx=a3; int 0x80.

section .text
global main.sysDebugWrite
main.sysDebugWrite:
    xor  eax, eax
    int  0x80
    ret

; ---------- Runtime stubs ----------

global runtime.alloc
runtime.alloc:
    ; Bump allocator over user stack page.
    mov  rax, qword [0x7FF000]
    test rax, rax
    jnz  .has_ptr
    mov  rax, 0x7FF008
.has_ptr:
    add  rdi, 7
    and  rdi, ~7
    lea  rdx, [rax + rdi]
    mov  qword [0x7FF000], rdx
    ret

global getrandom
getrandom:
    xor  eax, eax
    ret

global tinygo_register_fatal_signals
tinygo_register_fatal_signals:
    ret

; ---------- C library stubs ----------

global memset
memset:
    push rdi
    mov  rax, rsi
    mov  rcx, rdx
    rep  stosb
    pop  rax
    ret

global memcpy
memcpy:
    mov  rax, rdi
    mov  rcx, rdx
    rep  movsb
    ret

global memmove
memmove:
    mov  rax, rdi
    cmp  rdi, rsi
    jbe  .fwd
    lea  rsi, [rsi + rdx - 1]
    lea  rdi, [rdi + rdx - 1]
    std
    mov  rcx, rdx
    rep  movsb
    cld
    ret
.fwd:
    mov  rcx, rdx
    rep  movsb
    ret

global write
write:
    mov  rdi, rsi
    mov  rsi, rdx
    xor  eax, eax
    int  0x80
    ret

global abort
abort:
    hlt
    jmp abort

global exit
exit:
    hlt
    jmp exit

global _exit
_exit:
    hlt
    jmp _exit
