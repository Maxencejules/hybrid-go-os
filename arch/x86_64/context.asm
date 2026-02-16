; Hybrid Go OS — context switch, thread trampoline, user mode trampoline
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

; ----------------------------------------------------------------
; user_mode_trampoline — enter ring 3 via iretq
; Called via context_switch's ret on a user thread's initial stack.
; Stack: [user_entry_rip] [user_stack_rsp]
; Builds iretq frame: SS, RSP, RFLAGS, CS, RIP
; ----------------------------------------------------------------

global user_mode_trampoline
user_mode_trampoline:
    pop     rdi             ; user entry RIP
    pop     rsi             ; user stack RSP

    push    0x1B            ; SS = user data (0x18 | RPL=3)
    push    rsi             ; RSP = user stack
    push    0x202           ; RFLAGS = IF=1
    push    0x23            ; CS = user code (0x20 | RPL=3)
    push    rdi             ; RIP = user entry point
    iretq

section .note.GNU-stack noalloc noexec nowrite progbits
