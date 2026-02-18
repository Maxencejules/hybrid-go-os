; Rugo x86_64 user-space startup + syscall wrappers + runtime stubs
; NASM elf64 — assembled separately, linked via TinyGo ldflags.
; Kernel loads code at VA 0x400000 (RWX); RSP pre-set by iretq.

bits 64
default rel

; ---------- Entry point ----------
section .text._start
global _start
extern main
_start:
    call main            ; TinyGo runtime.main (C symbol "main")
    hlt                  ; GPF in ring 3 -> kernel catches, exits QEMU
    jmp _start

; ---------- Syscall wrappers ----------
; TinyGo C ABI (System V AMD64): rdi, rsi, rdx, rcx, r8, r9.
; Rugo syscall: rax=nr, rdi=a1, rsi=a2, rdx=a3;  int 0x80.

section .text
global main.sysDebugWrite
main.sysDebugWrite:
    ; rdi=buf, rsi=n -> rax=written
    xor  eax, eax
    int  0x80
    ret

global main.sysIpcSend
main.sysIpcSend:
    ; rdi=ep, rsi=buf, rdx=n -> rax
    mov  eax, 8
    int  0x80
    ret

global main.sysIpcRecv
main.sysIpcRecv:
    ; rdi=ep, rsi=buf, rdx=cap -> rax
    mov  eax, 9
    int  0x80
    ret

global main.sysSvcLookup
main.sysSvcLookup:
    ; rdi=name, rsi=len -> rax=endpoint
    mov  eax, 12
    int  0x80
    ret

; ---------- Runtime stubs ----------

global runtime.alloc
runtime.alloc:
    ; Bump allocator using stack page (0x7FF000, mapped RW).
    ; Heap pointer stored at 0x7FF000; data starts at 0x7FF008.
    ; Stack grows down from 0x800000 — no collision for small allocs.
    ; rdi = size -> rax = pointer
    mov  rax, qword [0x7FF000]
    test rax, rax
    jnz  .has_ptr
    mov  rax, 0x7FF008
.has_ptr:
    mov  rcx, rax
    add  rdi, 7
    and  rdi, ~7                 ; align size up to 8 bytes
    lea  rdx, [rax + rdi]
    mov  qword [0x7FF000], rdx   ; save next free
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
