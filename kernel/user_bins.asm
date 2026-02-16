; Embedded user-mode binaries (incbin from out/)
bits 64
section .rodata

global user_init_start
global user_init_size
global user_fault_start
global user_fault_size
global user_ping_start
global user_ping_size
global user_pong_start
global user_pong_size
global user_shm_writer_start
global user_shm_writer_size
global user_shm_reader_start
global user_shm_reader_size

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

user_ping_start:
    incbin "../out/ping.bin"
user_ping_end:
user_ping_size:
    dq user_ping_end - user_ping_start

user_pong_start:
    incbin "../out/pong.bin"
user_pong_end:
user_pong_size:
    dq user_pong_end - user_pong_start

user_shm_writer_start:
    incbin "../out/shm_writer.bin"
user_shm_writer_end:
user_shm_writer_size:
    dq user_shm_writer_end - user_shm_writer_start

user_shm_reader_start:
    incbin "../out/shm_reader.bin"
user_shm_reader_end:
user_shm_reader_size:
    dq user_shm_reader_end - user_shm_reader_start

section .note.GNU-stack noalloc noexec nowrite progbits
