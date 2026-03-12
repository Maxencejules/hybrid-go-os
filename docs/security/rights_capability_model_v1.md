# Rights and Capability Model v1

Date: 2026-03-04  
Milestone: M10

## Scope

Define the M10 least-privilege baseline for user-accessible handles in the
Rugo M3 compatibility path and the default Go service lane.

## Rights model

Per-handle rights are explicit and enforced on each syscall path.

### Rights bitset

- `READ` (`1`)
- `WRITE` (`2`)
- `POLL` (`4`)

### Object maxima

- console descriptor: `WRITE | POLL`
- compatibility file descriptor (`/compat/hello.txt`): `READ | POLL`

### Enforcement rules

- Rights are attached to each fd table entry.
- `sys_read` requires `READ`.
- `sys_write` requires `WRITE`.
- `sys_poll` requires `POLL` and event-compatible rights.
- Unauthorized operations return deterministic `-1`.

## Reduction and transfer semantics

M10 adds syscall-level capability operations:

- `sys_fd_rights_get(fd)` -> current rights bitset.
- `sys_fd_rights_reduce(fd, rights)` -> in-place monotonic reduction.
- `sys_fd_rights_transfer(fd, rights)` -> move handle to a new fd with reduced
  rights; source handle is revoked.

Rules:

- Rights can only shrink, never grow.
- Transfer cannot request rights outside the source handle rights.
- Reserved stdio descriptors (`0..2`) cannot be reduced/transferred.

## Default Go service lane object rights

The default Go service lane now enforces owner-scoped control on the R4 IPC
objects it actually uses:

- endpoint receive rights are owner-only in the `go_test` lane
- service registration/control rights are owner-only in the `go_test` lane
- service launch (`sys_thread_spawn_r4`) is restricted to the init task in the
  `go_test` lane
- policy violations are surfaced to the default Go services as deterministic
  `-1` failures

This keeps the manifest-driven init/service runtime honest without changing the
older R4 compatibility test contracts that still use shared raw endpoint ids.

## Kernel evidence

- Enforcement and storage:
  - `kernel_rs/src/lib.rs` (`M8FdEntry.rights`, `sys_read_v1`, `sys_write_v1`,
    `sys_poll_v1`)
- Default Go lane object controls:
  - `kernel_rs/src/lib.rs` (`R4Task.can_spawn`, `IpcEndpoint.owner_tid`,
    `IpcEndpoint.owner_rights`, `sys_ipc_recv_r4`, `sys_svc_register_r4`,
    `sys_thread_spawn_r4`)
- Capability syscalls:
  - `sys_fd_rights_get_v1`
  - `sys_fd_rights_reduce_v1`
  - `sys_fd_rights_transfer_v1`

## Executable checks

- `tests/security/test_rights_enforcement.py`
- `tests/security/test_go_service_policy_rights_v1.py`
- `tests/security/test_security_contract_docs_v1.py`
