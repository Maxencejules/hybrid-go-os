; Hybrid Go OS — ISR stubs, GDT/IDT flush, page fault test
; x86-64 NASM

bits 64
default rel

section .text

extern trap_handler

; ----------------------------------------------------------------
; Macros for ISR stubs
; ----------------------------------------------------------------

%macro ISR_NOERR 1
isr%1:
    push    0               ; dummy error code
    push    %1              ; interrupt number
    jmp     isr_common
%endmacro

%macro ISR_ERR 1
isr%1:
    push    %1              ; interrupt number (error code already on stack)
    jmp     isr_common
%endmacro

; ----------------------------------------------------------------
; 32 ISR stubs (exceptions 0-31)
; ----------------------------------------------------------------

ISR_NOERR 0     ; #DE  Divide Error
ISR_NOERR 1     ; #DB  Debug
ISR_NOERR 2     ; NMI
ISR_NOERR 3     ; #BP  Breakpoint
ISR_NOERR 4     ; #OF  Overflow
ISR_NOERR 5     ; #BR  Bound Range
ISR_NOERR 6     ; #UD  Invalid Opcode
ISR_NOERR 7     ; #NM  Device Not Available
ISR_ERR   8     ; #DF  Double Fault
ISR_NOERR 9     ; (reserved)
ISR_ERR   10    ; #TS  Invalid TSS
ISR_ERR   11    ; #NP  Segment Not Present
ISR_ERR   12    ; #SS  Stack-Segment Fault
ISR_ERR   13    ; #GP  General Protection
ISR_ERR   14    ; #PF  Page Fault
ISR_NOERR 15    ; (reserved)
ISR_NOERR 16    ; #MF  x87 FP Exception
ISR_ERR   17    ; #AC  Alignment Check
ISR_NOERR 18    ; #MC  Machine Check
ISR_NOERR 19    ; #XM  SIMD FP Exception
ISR_NOERR 20    ; #VE  Virtualization Exception
ISR_ERR   21    ; #CP  Control Protection
ISR_NOERR 22
ISR_NOERR 23
ISR_NOERR 24
ISR_NOERR 25
ISR_NOERR 26
ISR_NOERR 27
ISR_NOERR 28    ; #HV  Hypervisor Injection
ISR_ERR   29    ; #VC  VMM Communication
ISR_ERR   30    ; #SX  Security Exception
ISR_NOERR 31

; ----------------------------------------------------------------
; 16 IRQ stubs (vectors 32-47, remapped by PIC)
; ----------------------------------------------------------------

ISR_NOERR 32    ; IRQ0  PIT timer
ISR_NOERR 33    ; IRQ1  Keyboard
ISR_NOERR 34    ; IRQ2  Cascade
ISR_NOERR 35    ; IRQ3  COM2
ISR_NOERR 36    ; IRQ4  COM1
ISR_NOERR 37    ; IRQ5  LPT2
ISR_NOERR 38    ; IRQ6  Floppy
ISR_NOERR 39    ; IRQ7  Spurious
ISR_NOERR 40    ; IRQ8  RTC
ISR_NOERR 41    ; IRQ9  Free
ISR_NOERR 42    ; IRQ10 Free
ISR_NOERR 43    ; IRQ11 Free
ISR_NOERR 44    ; IRQ12 PS/2 Mouse
ISR_NOERR 45    ; IRQ13 FPU
ISR_NOERR 46    ; IRQ14 Primary ATA
ISR_NOERR 47    ; IRQ15 Secondary ATA

; ----------------------------------------------------------------
; Common ISR handler
; ----------------------------------------------------------------

isr_common:
    push    rax
    push    rbx
    push    rcx
    push    rdx
    push    rsi
    push    rdi
    push    rbp
    push    r8
    push    r9
    push    r10
    push    r11
    push    r12
    push    r13
    push    r14
    push    r15

    mov     rdi, rsp
    call    trap_handler

    pop     r15
    pop     r14
    pop     r13
    pop     r12
    pop     r11
    pop     r10
    pop     r9
    pop     r8
    pop     rbp
    pop     rdi
    pop     rsi
    pop     rdx
    pop     rcx
    pop     rbx
    pop     rax

    add     rsp, 16         ; remove int_num + error_code
    iretq

; ----------------------------------------------------------------
; gdt_flush — load GDT, reload segments, load TSS
; rdi = pointer to GDTR
; ----------------------------------------------------------------

global gdt_flush
gdt_flush:
    lgdt    [rdi]

    mov     ax, 0x10
    mov     ds, ax
    mov     es, ax
    mov     fs, ax
    mov     gs, ax
    mov     ss, ax

    ; Far jump to reload CS
    push    0x08
    lea     rax, [rel .reload_cs]
    push    rax
    retfq

.reload_cs:
    mov     ax, 0x18
    ltr     ax
    ret

; ----------------------------------------------------------------
; idt_flush — load IDT
; rdi = pointer to IDTR
; ----------------------------------------------------------------

global idt_flush
idt_flush:
    lidt    [rdi]
    ret

; ----------------------------------------------------------------
; test_trigger_page_fault — trigger a controlled PF for testing
; ----------------------------------------------------------------

global test_trigger_page_fault
test_trigger_page_fault:
    lea     rax, [rel .recovery]
    mov     [rel pf_recovery_rip], rax
    mov     rax, 0xDEAD0000
    mov     al, [rax]
.recovery:
    ret

; ----------------------------------------------------------------
; Data
; ----------------------------------------------------------------

section .bss
global pf_recovery_rip
pf_recovery_rip:
    resq    1

section .data
global isr_stub_table
isr_stub_table:
    dq isr0,  isr1,  isr2,  isr3,  isr4,  isr5,  isr6,  isr7
    dq isr8,  isr9,  isr10, isr11, isr12, isr13, isr14, isr15
    dq isr16, isr17, isr18, isr19, isr20, isr21, isr22, isr23
    dq isr24, isr25, isr26, isr27, isr28, isr29, isr30, isr31
    dq isr32, isr33, isr34, isr35, isr36, isr37, isr38, isr39
    dq isr40, isr41, isr42, isr43, isr44, isr45, isr46, isr47

section .note.GNU-stack noalloc noexec nowrite progbits
