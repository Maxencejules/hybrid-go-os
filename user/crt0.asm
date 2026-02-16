bits 64
section .text

extern main

global _start
_start:
    call    main

    ; sys_thread_exit
    mov     rax, 2
    int     0x80

.halt:
    cli
    hlt
    jmp     .halt

section .note.GNU-stack noalloc noexec nowrite progbits
