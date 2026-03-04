BITS 64

%define SYS_DEBUG_WRITE      0
%define SYS_VM_MAP           4
%define SYS_TIME_NOW         10
%define SYS_OPEN             18
%define SYS_PROFILE_SET      27
%define SYS_DEBUG_EXIT       98

_start:
    ; sys_sec_profile_set(RESTRICTED=1) -> 0
    mov edi, 1
    mov eax, SYS_PROFILE_SET
    int 0x80
    cmp rax, 0
    jne fail

    ; sys_vm_map must be blocked by profile -> -1
    mov edi, 0x00500000
    mov esi, 0x1000
    mov eax, SYS_VM_MAP
    int 0x80
    cmp rax, -1
    jne fail

    ; open("/dev/console", O_WRONLY, 0) must be blocked by profile -> -1
    lea rdi, [rel path_console]
    mov esi, 1
    xor edx, edx
    mov eax, SYS_OPEN
    int 0x80
    cmp rax, -1
    jne fail

    ; allowed syscall still works
    mov eax, SYS_TIME_NOW
    int 0x80
    cmp rax, -1
    je fail

    ; success marker
    lea rdi, [rel marker_ok]
    mov esi, 15
    mov eax, SYS_DEBUG_WRITE
    int 0x80

    mov edi, 0x31
    mov eax, SYS_DEBUG_EXIT
    int 0x80
    hlt

fail:
    mov edi, 0x33
    mov eax, SYS_DEBUG_EXIT
    int 0x80
    hlt

path_console:   db "/dev/console", 0
marker_ok:      db "SEC: filter ok", 10
