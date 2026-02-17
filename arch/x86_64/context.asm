; Rugo — context switch and thread entry trampoline
; x86-64 NASM

bits 64
default rel

section .text

; ----------------------------------------------------------------
; context_switch — swap kernel stacks
; rdi = &old_thread->rsp (pointer to save current RSP)
; rsi = new_thread->rsp  (value to load as new RSP)
; ----------------------------------------------------------------

global context_switch
context_switch:
    push    rbp
    push    rbx
    push    r12
    push    r13
    push    r14
    push    r15

    mov     [rdi], rsp      ; save old RSP
    mov     rsp, rsi        ; load new RSP

    pop     r15
    pop     r14
    pop     r13
    pop     r12
    pop     rbx
    pop     rbp
    ret

; ----------------------------------------------------------------
; thread_entry_trampoline — enable interrupts and jump to thread func
; Called via context_switch's ret on a new thread's initial stack.
; Stack: [func_addr] [thread_exit_addr]
; ----------------------------------------------------------------

global thread_entry_trampoline
thread_entry_trampoline:
    sti
    ret                     ; pops func addr -> starts thread

section .note.GNU-stack noalloc noexec nowrite progbits
