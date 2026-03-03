; Rugo x86_64 user-space startup stubs for the G2 std-port spike target.

bits 64
default rel

section .text._start
global _start
extern main
_start:
    call main
    hlt
    jmp _start
