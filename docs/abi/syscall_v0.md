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

| # | Name | Args | Returns | Status (R4) | Description |
|---|------|------|---------|-------------|-------------|
| 0 | sys_debug_write | rdi=buf, rsi=len | bytes written | Implemented (M3) | Write user buffer to serial (max 256 bytes, validates pointer) |
| 1 | sys_thread_spawn | rdi=entry | tid or -1 | Stub | Spawn user thread |
| 2 | sys_thread_exit | -- | -- | Stub | Terminate current thread |
| 3 | sys_yield | -- | 0 | Stub | Yield CPU to scheduler |
| 4 | sys_vm_map | rdi=vaddr, rsi=size | 0 or -1 | Stub | Map memory |
| 5 | sys_vm_unmap | rdi=vaddr, rsi=size | 0 or -1 | Stub | Unmap memory |
| 6 | sys_shm_create | rdi=size | shm_handle or -1 | **Implemented (R4)** | Create shared memory region (max 4096 bytes) |
| 7 | sys_shm_map | rdi=shm_handle, rsi=addr_hint, rdx=flags | mapped_addr or -1 | **Implemented (R4)** | Map shared memory into caller's address space |
| 8 | sys_ipc_send | rdi=endpoint, rsi=buf, rdx=len | 0 or -1 | **Implemented (R4)** | Send message to IPC endpoint (max 256 bytes) |
| 9 | sys_ipc_recv | rdi=endpoint, rsi=buf, rdx=cap | bytes_received or -1 | **Implemented (R4)** | Receive from IPC endpoint (blocks if empty) |
| 10 | sys_time_now | -- | tick count | Implemented (M3) | Current monotonic tick count |
| 11 | sys_svc_register | rdi=name_ptr, rsi=name_len, rdx=endpoint | 0 or -1 | **Implemented (R4)** | Register service name → endpoint mapping |
| 12 | sys_svc_lookup | rdi=name_ptr, rsi=name_len | endpoint or -1 | **Implemented (R4)** | Lookup service endpoint by name |

Stubs return -1 (0xFFFFFFFFFFFFFFFF) and will be implemented in later milestones.

## IPC model (R4)

### Endpoints

- IPC endpoints are identified by small integer IDs (0–3).
- Each endpoint has a single-slot message buffer (max 256 bytes per message).
- Only one message can be buffered per endpoint at a time.

### Blocking semantics

- `sys_ipc_recv` blocks if no message is available. The kernel saves the
  caller's state and switches to the next ready task.
- `sys_ipc_send` is non-blocking. If a task is blocked on recv for the
  target endpoint, the message is delivered directly to the waiter's
  buffer and the waiter is marked ready.
- If no waiter exists, the message is stored in the endpoint's buffer.

### Message format

Messages are opaque byte sequences. The kernel does not interpret payload
contents. Sender and receiver agree on format by convention.

## Shared memory model (R4)

### Create

- `sys_shm_create(size)` allocates a kernel-backed page (up to 4096 bytes).
- Returns a handle (small integer 0–1).
- The kernel zero-initializes the backing page.

### Map

- `sys_shm_map(handle, addr_hint, flags)` installs user-accessible PTEs
  pointing to the shared physical page.
- `addr_hint` specifies the desired virtual address (must be page-aligned
  and in user range).
- Returns the mapped virtual address on success.
- Multiple tasks can map the same handle; they share the same physical page.

### Constraints

- Maximum 2 SHM regions.
- Each region is exactly one 4K page.
- `flags` is reserved (must be 0).

## Service registry (R4)

- Kernel-side name→endpoint lookup table (4 slots max).
- `sys_svc_register` stores a mapping; `sys_svc_lookup` retrieves it.
- Names are compared byte-for-byte (up to 16 bytes).
- Duplicate registrations overwrite the previous entry.

## User pointer safety (M3+)

For syscalls that touch user memory:
1. Buffer must be in user address range (below 0x0000_8000_0000_0000).
2. Pages must be present and user-accessible (kernel walks page tables).
3. At most 256 bytes are copied to a kernel buffer before processing.
4. On validation failure, the syscall returns -1 without crashing.

## User fault containment (M3+)

If a page fault or GPF occurs while CS indicates ring 3 (user mode):
- The kernel terminates the user task.
- In M3 tests: prints `USER: killed` and continues kernel execution.
- In R4 tests: silently kills the task and schedules the next ready task.
  When no tasks remain, the kernel exits.

## Notes

- M3/R4 use `int 0x80` (software interrupt) rather than the `SYSCALL`/`SYSRET`
  MSR mechanism. This simplifies the first user-mode bringup.
- Ring 3 entry is via `iretq` with proper user CS/SS selectors.
- Interrupts may be disabled in user mode for M3/R4. Syscalls and faults still work.
- R4 uses cooperative two-task scheduling: tasks switch only on blocking
  syscalls (ipc_recv) or task death (fault/halt).
