# Syscall ABI v1

## Lane

Rugo (Rust no_std kernel). This ABI applies to the Rugo lane only.

## Status

Draft contract established in M8 PR-1 on 2026-03-04. This document is the
compatibility baseline for future M8 implementation PRs.

## Relationship to v0

- v1 keeps the same invocation mechanism as v0 (`int 0x80`).
- v1 keeps the same register calling convention as v0.
- Existing syscall IDs `0..17` remain reserved and compatible in v1.x.
- `docs/abi/syscall_v0.md` remains historical baseline; v1 is the active
  compatibility contract for M8 work.

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

The kernel preserves all callee-saved registers (`rbx`, `rbp`, `r12-r15`,
`rsp`). Caller-saved registers (`rcx`, `r11`) may be clobbered. Return values
overwrite `rax`.

## Versioning and compatibility rules

### Contract identity

A syscall contract is defined by:

1. syscall ID,
2. argument registers and meaning,
3. return-value model,
4. side-effect guarantees (including failure-path guarantees).

Changing any of those is a breaking change and is not allowed in `v1.x`.

### Stability rules for v1.x

- Stable syscall IDs in v1.x cannot be renumbered.
- Existing argument meaning cannot be repurposed.
- Breaking behavioral changes are disallowed.
- New syscalls must be additive (new ID only).
- New optional features must fail deterministically when unavailable.

### Syscall ID policy

- `0..31`: core runtime/process/file/network primitives.
- `32..127`: future stable extensions.
- `128..255`: experimental range; no compatibility promise.

IDs in the experimental range must not be required by Compatibility Profile v1.

### Compatibility classes

- `required`: must be implemented for Compatibility Profile v1 conformance.
- `optional`: may be absent; absence must fail deterministically.
- `experimental`: may change without compatibility guarantees.

## Deterministic error model

### Return encoding

For v1.0, syscall error return remains `(u64)-1` (`0xFFFF_FFFF_FFFF_FFFF`).
Success remains non-negative return values.

### Determinism requirements

- Same input + same kernel state yields the same success/error outcome.
- Validation failures (`bad pointer`, `bad length`, `bad flags`) must not
  partially mutate kernel state.
- Non-blocking operations must return immediately with deterministic outcome.
- Unsupported operations must fail as unsupported (not silently emulate).

### Canonical error classes

The following symbolic classes define normative behavior for docs/tests:

| Class | Meaning |
|-------|---------|
| `E_INVAL` | Invalid argument value/combination |
| `E_RANGE` | Value outside supported range/limits |
| `E_FAULT` | User pointer invalid or inaccessible |
| `E_BUSY` | Resource temporarily busy |
| `E_AGAIN` | Transient condition, retry is valid |
| `E_PERM` | Permission/capability denied |
| `E_UNSUP` | Operation intentionally unsupported in this profile |
| `E_NOSYS` | Unknown or unavailable syscall ID |
| `E_IO` | Device or transport I/O failure |
| `E_TIMEOUT` | Bounded operation timed out |

v1.0 exposes these classes through deterministic behavior and test markers while
keeping the ABI return code as `-1`. A future v1.x extension may add an
explicit reason-code channel in an additive way.

## Deprecation policy

### Lifecycle states

- `active`: fully supported and covered by compatibility tests.
- `deprecated`: still supported; replacement is documented.
- `removed`: available only in the next major ABI line (`v2+`), never within
  `v1.x`.

### Rules

- A syscall must stay behavior-compatible while deprecated.
- Deprecation notice must include:
  - first deprecation version/date,
  - replacement path,
  - earliest planned removal major version.
- Minimum deprecation window: two tagged releases in `v1.x`.
- Removal from compatibility profile is only allowed in the next major line.

## Baseline inherited from v0 (2026-03-04)

These IDs are carried forward unchanged into the v1 line:

| # | Name |
|---|------|
| 0 | `sys_debug_write` |
| 1 | `sys_thread_spawn` |
| 2 | `sys_thread_exit` |
| 3 | `sys_yield` |
| 4 | `sys_vm_map` |
| 5 | `sys_vm_unmap` |
| 6 | `sys_shm_create` |
| 7 | `sys_shm_map` |
| 8 | `sys_ipc_send` |
| 9 | `sys_ipc_recv` |
| 10 | `sys_time_now` |
| 11 | `sys_svc_register` |
| 12 | `sys_svc_lookup` |
| 13 | `sys_blk_read` |
| 14 | `sys_blk_write` |
| 15 | `sys_net_send` |
| 16 | `sys_net_recv` |
| 17 | `sys_ipc_endpoint_create` |

## Core compatibility extensions in v1 (M8 PR-2)

These syscall IDs are added for the Compatibility Profile v1 baseline in PR-2.
They are defined as stable in the v1.x line.

| # | Name | Args | Returns | PR-2 status |
|---|------|------|---------|-------------|
| 18 | `sys_open` | `rdi=path_ptr`, `rsi=flags`, `rdx=mode` | `fd` or `-1` | Implemented (v1 baseline paths: `/dev/console`, `/compat/hello.txt`) |
| 19 | `sys_read` | `rdi=fd`, `rsi=buf`, `rdx=len` | bytes read or `-1` | Implemented (deterministic fd-table v1 behavior) |
| 20 | `sys_write` | `rdi=fd`, `rsi=buf`, `rdx=len` | bytes written or `-1` | Implemented (console write path; deterministic errors) |
| 21 | `sys_close` | `rdi=fd` | `0` or `-1` | Implemented |
| 22 | `sys_wait` | `rdi=pid`, `rsi=status_ptr`, `rdx=options` | child pid or `-1` | Implemented (wait baseline semantics) |
| 23 | `sys_poll` | `rdi=pollfd_ptr`, `rsi=nfds`, `rdx=timeout_ticks` | ready count or `-1` | Implemented (poll baseline equivalent wait primitive) |

## Security baseline extensions in v1 (M10)

These syscall IDs add M10 least-privilege controls and are stable in v1.x.

| # | Name | Args | Returns | M10 status |
|---|------|------|---------|------------|
| 24 | `sys_fd_rights_get` | `rdi=fd` | rights bitset or `-1` | Implemented |
| 25 | `sys_fd_rights_reduce` | `rdi=fd`, `rsi=rights_mask` | `0` or `-1` | Implemented (monotonic reduction only) |
| 26 | `sys_fd_rights_transfer` | `rdi=fd`, `rsi=rights_mask` | new fd or `-1` | Implemented (source fd revoked on success) |
| 27 | `sys_sec_profile_set` | `rdi=profile_id` | `0` or `-1` | Implemented (`0=default`, `1=restricted`) |

## C3 process and scheduler control extensions

These syscall IDs expose the contracted process/accounting and scheduler-control
surface used by the default Go service lane. They are additive in `v1.x` and
currently exercised on the `go_test` boot path.

| # | Name | Args | Returns | C3 status |
|---|------|------|---------|-----------|
| 28 | `sys_proc_info` | `rdi=tid`, `rsi=info_ptr`, `rdx=info_len` | `0` or `-1` | Implemented on the default Go lane for task identity, parent, state, scheduler class, and accounting snapshots |
| 29 | `sys_sched_set` | `rdi=tid`, `rsi=class_id` | `0` or `-1` | Implemented on the default Go lane for bounded scheduler-class control (`0=best-effort`, `1=critical`) |

## Related contracts

- Process/thread + loader + auxv + argv/envp contract:
  `docs/abi/process_thread_model_v1.md`
- Compatibility profile surface:
  `docs/abi/compat_profile_v1.md`
- Rights/capability contract:
  `docs/security/rights_capability_model_v1.md`
- Syscall filtering contract:
  `docs/security/syscall_filtering_v1.md`

## Conformance references

- `docs/abi/process_thread_model_v1.md`
- `docs/abi/compat_profile_v1.md`
- `tests/compat/`
