# Syscall ABI v2

## Lane

Rugo (Rust `no_std` kernel). This ABI applies to the Rugo lane only.

## Status

Active contract closed in M17 on 2026-03-06.

## Contract identity

Syscall ABI identifier: `rugo.syscall_abi.v2`.

## Relationship to v1

- Invocation mechanism and register convention are unchanged from v1.
- Syscall IDs `0..27` are carried forward without renumbering.
- Compatibility Profile v2 is the active consumer contract in M17.
- IDs `28..31` are reserved for additive v2.x expansion and are not required in
  v2.0.

## Invocation

Use `int 0x80` (vector 128, DPL=3).

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

## v2 freeze and deprecation rules

- Freeze window: v2.x.
- No syscall ID renumbering is allowed in v2.x.
- Existing argument semantics and side effects cannot change in v2.x.
- New behavior in v2.x must be additive only.
- Deprecation requires:
  - documented replacement path,
  - first deprecation version/date,
  - minimum two tagged releases before removal in v3.

## Deterministic error classes

`-1` remains the error return encoding. Error classes are contract-level labels
for deterministic behavior:

| Class | Meaning |
|-------|---------|
| `E_INVAL` | Invalid argument combination |
| `E_RANGE` | Value outside supported limits |
| `E_FAULT` | Invalid user pointer/range |
| `E_BUSY` | Resource is temporarily busy |
| `E_AGAIN` | Retry is allowed |
| `E_PERM` | Rights/capability denied |
| `E_UNSUP` | Explicitly unsupported operation |
| `E_NOSYS` | Unknown syscall ID |
| `E_IO` | Device/transport I/O failure |
| `E_TIMEOUT` | Bounded operation timed out |

Unsupported operations must fail deterministically (`E_UNSUP`/`E_NOSYS`), never
silently emulate.

## Compatibility classes for v2 profile

- `required`: mandatory for `compat_profile_v2`.
- `optional`: may be absent in v2.0; absence must fail deterministically.
- `unsupported`: explicitly out of profile scope.

## v2 required syscall surface (M17)

| ID | Name | Class | Notes |
|----|------|-------|-------|
| 0 | `sys_debug_write` | required | logging/debug baseline |
| 1 | `sys_thread_spawn` | required | runtime thread bringup path |
| 2 | `sys_thread_exit` | required | runtime thread teardown |
| 3 | `sys_yield` | required | scheduler cooperation primitive |
| 4 | `sys_vm_map` | required | runtime mapping path |
| 5 | `sys_vm_unmap` | required | runtime unmap path |
| 10 | `sys_time_now` | required | monotonic/realtime baseline |
| 18 | `sys_open` | required | file-open baseline |
| 19 | `sys_read` | required | file/socket read baseline |
| 20 | `sys_write` | required | file/socket write baseline |
| 21 | `sys_close` | required | descriptor lifecycle |
| 22 | `sys_wait` | required | process wait lifecycle |
| 23 | `sys_poll` | required | readiness wait baseline |
| 24 | `sys_fd_rights_get` | required | security/read rights introspection |
| 25 | `sys_fd_rights_reduce` | required | monotonic rights reduction |
| 26 | `sys_fd_rights_transfer` | required | rights transfer baseline |
| 27 | `sys_sec_profile_set` | required | restricted profile switch |

## Explicitly non-required in v2.0

- `6..9`, `11..17`: optional/deferred for this profile window.
- Future v2.x additions must remain additive and backward compatible.

## Conformance references

- `docs/abi/compat_profile_v2.md`
- `docs/abi/elf_loader_contract_v2.md`
- `docs/runtime/syscall_coverage_matrix_v2.md`
- `tests/compat/test_abi_profile_v2_docs.py`
- `tests/compat/test_posix_profile_v2.py`

