# Syscall Filtering Framework v1

Date: 2026-03-04  
Milestone: M10

## Scope

Define per-process syscall sandbox profiles for the M3 compatibility runtime.

## Profiles

- `0`: `Default` profile
- `1`: `Restricted` profile

The active profile is set through:

- `sys_sec_profile_set(profile_id)` (`syscall 27`)

## Default profile

- All currently implemented M3 syscall IDs remain available.
- Backward-compatible behavior is preserved for existing milestone tests.

## Restricted profile

Restricted profile enforces a least-privilege syscall allowlist:

- allowed: `0`, `2`, `3`, `10`, `18..27`, `98` (test-only debug exit)
- denied: all other syscall IDs (deterministic `-1`)

Additional resource policy:

- path gate on `sys_open`:
  - allowed: `/compat/hello.txt`
  - denied: `/dev/console` and all other paths

## Deterministic behavior requirements

- Forbidden syscall IDs return `-1`.
- Forbidden resource paths return `-1`.
- Allowed syscalls retain deterministic semantics.

## Kernel evidence

- `kernel_rs/src/lib.rs`:
  - `M10SecProfile`
  - `m10_syscall_allowed`
  - `m10_profile_path_allowed`
  - `sys_sec_profile_set_v1`

## Executable checks

- `tests/security/test_syscall_filter.py`
- `tests/security/test_security_contract_docs_v1.py`
