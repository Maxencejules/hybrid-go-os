# Compatibility Profile v2

## Lane

Rugo (Rust kernel + Go user space).

## Status

Profile v2 closed in M17 on 2026-03-06.

## Contract identity

Compatibility profile identifier: `rugo.compat_profile.v2`.

## Goal

Increase external software viability with:

- explicit required vs optional vs unsupported syscall surfaces,
- deterministic ELF loader behavior for static and dynamic binaries,
- deterministic external app tier thresholds backed by signed artifacts.

This remains a compatibility subset, not full Linux ABI parity.

## Profile classes

- `required`: mandatory for v2 profile conformance.
- `optional`: may be absent in v2.0; absence must fail deterministically.
- `unsupported`: explicitly out of scope and must fail deterministically.

## Required subset (`required`)

### Process and loader subset (`required`)

- Deterministic `execve`-style startup contract (`argv`/`envp` + aux-vector).
- Deterministic `wait` lifecycle behavior.
- Deterministic ELF loader contract with:
  - static ELF (`ET_EXEC`) baseline,
  - dynamic ELF (`ET_DYN`) baseline when v2 loader rules are satisfied.

Conformance coverage:
- `tests/compat/test_abi_profile_v2_docs.py`
- `tests/compat/test_elf_loader_dynamic_v2.py`

### File descriptor and I/O subset (`required`)

- `open`, `read`, `write`, `close`.
- Descriptor rights APIs (`sys_fd_rights_*`) and profile selector syscall.
- Poll/readiness baseline via `sys_poll`.

Conformance coverage:
- `tests/compat/test_posix_profile_v2.py`
- `tests/compat/test_compat_gate_v2.py`

### Time and signal subset (`required`)

- `clock_gettime` and `nanosleep` baseline semantics.
- Deterministic signal delivery/queue handling in the profiled surface.

Conformance coverage:
- `tests/compat/test_posix_profile_v2.py`

### Socket subset (`required`)

- `socket`, `bind`, `listen`, `accept`, `connect`.
- `send`/`recv`, `sendto`/`recvfrom`, `shutdown`.
- Readiness wait through `poll` baseline.

Conformance coverage:
- `tests/compat/test_posix_profile_v2.py`

## Optional subset (`optional`)

- `fork`-like process cloning semantics.
- `accept4`, `clock_nanosleep`, and advanced signal option flags.
- Additional IPC/service registry expansion beyond current v2 subset.

Optional APIs must return deterministic unsupported behavior when absent.

## Explicit unsupported list (`unsupported`)

The following remain out of scope for v2:

- `epoll`, `io_uring`, `fanotify`, `inotify`, `eventfd`, `timerfd`,
- Linux namespace/cgroup/seccomp compatibility layers,
- full `AF_UNIX` parity and `AF_NETLINK`,
- desktop/GUI ABI surfaces.

## External application tiers

Signed artifact inputs are mandatory.

Tier A (`required`): signed static CLI payloads.
- Inputs: signed package metadata + deterministic static payload.
- Expected runtime markers: package integrity + app marker.

Tier B (`required`): signed dynamic/runtime payloads.
- Inputs: signed package metadata + dynamic/runtime loader contract compliance.
- Expected runtime markers: standard runtime lane marker (`GOSTD: ok`) and
  deterministic report output.

### Tier thresholds

| Tier | Minimum signed cases | Minimum pass rate |
|------|----------------------|-------------------|
| `tier_a` | 12 | 0.90 |
| `tier_b` | 8 | 0.75 |

Additional gate rules:

- Any unsigned artifact is gate-failing.
- Any non-deterministic case result is gate-failing.
- ABI profile mismatch (`compat_profile_v2` expected) is gate-failing.

## Conformance and release gate

Local gate: `make test-compat-v2`.

Gate test inventory:
- `tests/compat/test_abi_profile_v2_docs.py`
- `tests/compat/test_elf_loader_dynamic_v2.py`
- `tests/compat/test_posix_profile_v2.py`
- `tests/compat/test_external_apps_tier_v2.py`
- `tests/compat/test_compat_gate_v2.py`

CI lane: step `Compatibility profile v2 gate`.

## Related contracts

- `docs/abi/syscall_v2.md`
- `docs/abi/elf_loader_contract_v2.md`
- `docs/runtime/syscall_coverage_matrix_v2.md`

