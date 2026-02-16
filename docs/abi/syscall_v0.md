# Syscall ABI v0

## Invocation

Use `int 0x80`. Syscall number in `rax`, arguments in `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9`. Return value in `rax`. Negative values indicate errors.

## Syscall Table

| # | Name | Args | Returns | Description |
|---|------|------|---------|-------------|
| 0 | sys_debug_write | rdi=buf, rsi=len | bytes written | Write buffer to serial |
| 1 | sys_thread_spawn | rdi=entry | tid or -1 | Spawn user thread (stub) |
| 2 | sys_thread_exit | — | — | Terminate current thread |
| 3 | sys_yield | — | 0 | Yield CPU to scheduler |
| 4 | sys_vm_map | rdi=vaddr, rsi=size | 0 or -1 | Map memory (stub) |
| 5 | sys_vm_unmap | rdi=vaddr, rsi=size | 0 or -1 | Unmap memory (stub) |
| 6 | sys_shm_create | rdi=size | shm_id or -1 | Create shared memory (stub) |
| 7 | sys_shm_map | rdi=shm_id, rsi=vaddr | 0 or -1 | Map shared memory (stub) |
| 8 | sys_ipc_send | rdi=dst_tid, rsi=buf | 0 or -1 | Send IPC message (stub) |
| 9 | sys_ipc_recv | rdi=buf, rsi=len | bytes or -1 | Receive IPC message (stub) |
| 10 | sys_time_now | — | tick count | Current PIT tick count |

Stubs return -1 and will be implemented in later milestones.
