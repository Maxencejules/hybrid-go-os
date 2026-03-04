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

## Conformance references

- `docs/abi/compat_profile_v1.md`
- `tests/compat/`
