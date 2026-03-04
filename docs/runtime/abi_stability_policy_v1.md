# Runtime ABI Stability Policy v1

Date: 2026-03-04  
Milestone: M11 Runtime + Toolchain Maturity v1  
Policy ID: `rugo.runtime_abi_policy.v1`

## Scope

This policy governs runtime-facing syscalls used by the stock-Go port lane and
the compatibility baseline that runtime integration depends on.

## Stability window

Stability window: `2026-03-04` through `2026-12-31` (v1 line).

Within this window:

- syscall numbers and argument meanings for runtime-facing symbols are frozen;
- success/failure behavior remains backward-compatible;
- removals are not allowed; only additive extensions are permitted.

## Runtime-facing frozen syscall set (v1 lane)

From `docs/abi/syscall_v0.md`:

- `sys_debug_write` (0)
- `sys_thread_spawn` (1)
- `sys_thread_exit` (2)
- `sys_yield` (3)
- `sys_vm_map` (4)
- `sys_vm_unmap` (5)
- `sys_time_now` (10)

From `docs/abi/syscall_v1.md` compatibility baseline:

- `sys_open` (18)
- `sys_read` (19)
- `sys_write` (20)
- `sys_close` (21)
- `sys_poll` (23)

## Deprecation and breakage process

1. Propose change in a design note linked from `docs/runtime/`.
2. Mark symbol state as `active` -> `deprecated` with replacement path.
3. Keep behavior compatible for at least two tagged v1 releases.
4. Remove only in a new major ABI line (`v2+`), never in `v1.x`.

## Release gate requirements

- `tests/runtime/test_runtime_abi_window_v1.py` validates policy/doc alignment.
- `tests/runtime/test_runtime_contract_docs_v1.py` validates gate wiring.
- `make test-runtime-maturity` must pass before release.
