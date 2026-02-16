; Embedded user-mode binaries (incbin from out/)
bits 64
section .rodata

global user_init_start
global user_init_size
global user_fault_start
global user_fault_size

user_init_start:
    incbin "../out/init.bin"
user_init_end:
user_init_size:
    dq user_init_end - user_init_start

user_fault_start:
    incbin "../out/fault.bin"
user_fault_end:
user_fault_size:
    dq user_fault_end - user_fault_start

section .note.GNU-stack noalloc noexec nowrite progbits
