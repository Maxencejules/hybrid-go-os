; arch/x86_64/isr.asm — ISR stubs for M1 exception handling
bits 64
default rel

section .text

extern exception_handler

; Macro for exceptions WITHOUT a CPU-pushed error code
%macro ISR_NOERR 1
global isr_stub_%1
isr_stub_%1:
    push qword 0           ; dummy error code
    push qword %1          ; vector number
    jmp isr_common
%endmacro

; Macro for exceptions WITH a CPU-pushed error code
%macro ISR_ERR 1
global isr_stub_%1
isr_stub_%1:
    push qword %1          ; vector number (error code already on stack)
    jmp isr_common
%endmacro

; --- Vector stubs ---
ISR_NOERR 0                ; #DE  Divide Error
ISR_NOERR 3                ; #BP  Breakpoint
ISR_ERR   8                ; #DF  Double Fault
ISR_ERR   13               ; #GP  General Protection Fault
ISR_ERR   14               ; #PF  Page Fault

; --- Common tail: marshal args and call Rust handler ---
;
; Stack layout on entry:
;   [RSP+0]   vector         (pushed by stub)
;   [RSP+8]   error code     (CPU or dummy 0)
;   [RSP+16]  RIP            (CPU interrupt frame)
;   [RSP+24]  CS
;   [RSP+32]  RFLAGS
;   [RSP+40]  RSP (old)
;   [RSP+48]  SS
isr_common:
    mov rdi, [rsp]          ; arg1: vector
    mov rsi, [rsp+8]        ; arg2: error_code
    mov rdx, [rsp+16]       ; arg3: rip
    mov rcx, cr2            ; arg4: fault address

    and rsp, -16            ; 16-byte align for SysV ABI call
    call exception_handler

    ; Should never return, but guard anyway
    cli
    hlt

section .note.GNU-stack noalloc noexec nowrite progbits
