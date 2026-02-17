; Hybrid Go OS — x86-64 kernel entry point
; Limine jumps here in 64-bit long mode with paging enabled.

bits 64
default rel

; --------------- BSS: kernel stack ---------------
section .bss
align 16
stack_bottom:
    resb 16384              ; 16 KiB kernel stack
stack_top:

; --------------- TEXT: entry ---------------
section .text
global _start
extern kmain

_start:
    cli                     ; Ensure interrupts are off
    lea  rsp, [stack_top]   ; Set up kernel stack
    xor  rbp, rbp           ; Clear frame pointer
    call kmain              ; Enter kernel (kernel/main.c)

.hang:
    cli
    hlt
    jmp  .hang

; Mark stack as non-executable (silences ld warning).
section .note.GNU-stack noalloc noexec nowrite progbits
