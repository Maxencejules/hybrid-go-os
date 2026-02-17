# Syscall ABI v0

## Lane

Rugo (Rust no_std kernel). This ABI applies to the Rugo lane only.

## Invocation

Use `int 0x80` (IDT vector 128, gate DPL=3 so user mode can invoke it).

### Register convention

| Register | Purpose |
|----------|---------|
| `rax` | Syscall number (in) / return value (out) |
| `rdi` | Argument 1 |
| `rsi` | Argument 2 |
| `rdx` | Argument 3 |
| `r10` | Argument 4 |
| `r8` | Argument 5 |
| `r9` | Argument 6 |

### Clobbered registers

The kernel preserves all callee-saved registers (rbx, rbp, r12-r15, rsp).
Caller-saved registers (rcx, r11) may be clobbered. The return value
overwrites rax.

### Return values

Non-negative values indicate success. The value `(u64)-1` (0xFFFFFFFFFFFFFFFF)
indicates an error.

## Syscall Table

| # | Name | Args | Returns | Status (M3) | Description |
|---|------|------|---------|-------------|-------------|
| 0 | sys_debug_write | rdi=buf, rsi=len | bytes written | Implemented | Write user buffer to serial (max 256 bytes, validates pointer) |
| 1 | sys_thread_spawn | rdi=entry | tid or -1 | Stub | Spawn user thread |
| 2 | sys_thread_exit | -- | -- | Stub | Terminate current thread |
| 3 | sys_yield | -- | 0 | Stub | Yield CPU to scheduler |
| 4 | sys_vm_map | rdi=vaddr, rsi=size | 0 or -1 | Stub | Map memory |
| 5 | sys_vm_unmap | rdi=vaddr, rsi=size | 0 or -1 | Stub | Unmap memory |
| 6 | sys_shm_create | rdi=size | shm_id or -1 | Stub | Create shared memory |
| 7 | sys_shm_map | rdi=shm_id, rsi=vaddr | 0 or -1 | Stub | Map shared memory |
| 8 | sys_ipc_send | rdi=dst_tid, rsi=buf | 0 or -1 | Stub | Send IPC message |
| 9 | sys_ipc_recv | rdi=buf, rsi=len | bytes or -1 | Stub | Receive IPC message |
| 10 | sys_time_now | -- | tick count | Implemented | Current monotonic tick count |

Stubs return -1 (0xFFFFFFFFFFFFFFFF) and will be implemented in later milestones.

## User pointer safety (M3)

For `sys_debug_write`, the kernel validates user pointers before access:
1. Buffer must be in user address range (below 0x0000_8000_0000_0000).
2. Pages must be present and user-accessible (kernel walks page tables).
3. At most 256 bytes are copied to a kernel buffer before printing.
4. On validation failure, the syscall returns -1 without crashing.

## User fault containment (M3)

If a page fault or GPF occurs while CS indicates ring 3 (user mode):
- The kernel terminates the user task.
- Prints `USER: killed` to serial.
- Continues running the kernel (does not panic).

## Notes

- M3 uses `int 0x80` (software interrupt) rather than the `SYSCALL`/`SYSRET`
  MSR mechanism. This simplifies the first user-mode bringup.
- Ring 3 entry is via `iretq` with proper user CS/SS selectors.
- Interrupts may be disabled in user mode for M3. Syscalls and faults still work.
