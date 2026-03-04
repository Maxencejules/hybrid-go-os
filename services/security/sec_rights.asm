BITS 64

%define SYS_DEBUG_WRITE         0
%define SYS_READ                19
%define SYS_WRITE               20
%define SYS_OPEN                18
%define SYS_FD_RIGHTS_GET       24
%define SYS_FD_RIGHTS_REDUCE    25
%define SYS_FD_RIGHTS_TRANSFER  26
%define SYS_DEBUG_EXIT          98

%define RIGHT_READ              1
%define RIGHT_WRITE             2
%define RIGHT_POLL              4

_start:
    ; fd_file = open("/compat/hello.txt", O_RDONLY, 0)
    lea rdi, [rel path_file]
    xor esi, esi
    xor edx, edx
    mov eax, SYS_OPEN
    int 0x80
    cmp rax, -1
    je fail
    mov r12, rax

    ; write(fd_file, "bad", 3) -> -1
    mov rdi, r12
    lea rsi, [rel msg_bad]
    mov edx, 3
    mov eax, SYS_WRITE
    int 0x80
    cmp rax, -1
    jne fail

    ; rights_get(fd_file) -> RIGHT_READ | RIGHT_POLL
    mov rdi, r12
    mov eax, SYS_FD_RIGHTS_GET
    int 0x80
    cmp rax, RIGHT_READ | RIGHT_POLL
    jne fail

    ; rights_reduce(fd_file, 0) -> 0
    mov rdi, r12
    xor esi, esi
    mov eax, SYS_FD_RIGHTS_REDUCE
    int 0x80
    cmp rax, 0
    jne fail

    ; read(fd_file, scratch, 1) -> -1
    mov rdi, r12
    lea rsi, [rel scratch]
    mov edx, 1
    mov eax, SYS_READ
    int 0x80
    cmp rax, -1
    jne fail

    ; fd_console = open("/dev/console", O_WRONLY, 0)
    lea rdi, [rel path_console]
    mov esi, 1
    xor edx, edx
    mov eax, SYS_OPEN
    int 0x80
    cmp rax, -1
    je fail
    mov r13, rax

    ; fd_new = rights_transfer(fd_console, RIGHT_WRITE)
    mov rdi, r13
    mov esi, RIGHT_WRITE
    mov eax, SYS_FD_RIGHTS_TRANSFER
    int 0x80
    cmp rax, -1
    je fail
    mov r14, rax

    ; old fd must be closed now: write(fd_console, "old!", 4) -> -1
    mov rdi, r13
    lea rsi, [rel msg_old]
    mov edx, 4
    mov eax, SYS_WRITE
    int 0x80
    cmp rax, -1
    jne fail

    ; new fd is writable: write(fd_new, "ok\n", 3) -> 3
    mov rdi, r14
    lea rsi, [rel msg_ok]
    mov edx, 3
    mov eax, SYS_WRITE
    int 0x80
    cmp rax, 3
    jne fail

    ; success marker
    lea rdi, [rel marker_ok]
    mov esi, 15
    mov eax, SYS_DEBUG_WRITE
    int 0x80

    ; qemu_exit(0x31)
    mov edi, 0x31
    mov eax, SYS_DEBUG_EXIT
    int 0x80
    hlt

fail:
    mov edi, 0x33
    mov eax, SYS_DEBUG_EXIT
    int 0x80
    hlt

path_file:      db "/compat/hello.txt", 0
path_console:   db "/dev/console", 0
msg_bad:        db "bad"
msg_old:        db "old!"
msg_ok:         db "ok", 10
marker_ok:      db "SEC: rights ok", 10
scratch:        db 0
