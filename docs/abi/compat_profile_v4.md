# Compatibility Profile v4

Date: 2026-03-09  
Milestone: M36 Compatibility Surface Expansion v1  
Status: active release gate

## Purpose

Expand compatibility coverage beyond v2/v3 subset boundaries while keeping
unsupported surfaces explicit and deterministically rejected.

## Contract identity

- Compatibility profile identifier: `rugo.compat_profile.v4`.
- Process model contract ID: `rugo.process_model.v3`.
- Socket family contract ID: `rugo.socket_family_expansion.v1`.
- POSIX gap report schema: `rugo.posix_gap_report.v1`.
- Compatibility surface campaign schema: `rugo.compat_surface_campaign_report.v1`.

## Profile classes

- `required`: release-blocking M36 compatibility commitments.
- `optional`: non-blocking expansion that may graduate in later milestones.
- `deferred`: explicitly not supported in v4 and must fail deterministically.

## Required surfaces (`required`)

### Process lifecycle

- `waitid`, `sigprocmask`, `sigpending`.
- deterministic spawn/exit/reap behavior bound to `process_model_v3`.

### Readiness and POSIX I/O gap closures

- `pselect`, `ppoll`, `sendmsg`, `recvmsg`.
- deterministic report coverage through `run_posix_gap_report_v1.py`.

### Socket family expansion

- `AF_INET` and `AF_INET6` baseline path remains required.
- bounded `AF_UNIX` stream/datagram subset is required.
- `socketpair` support is required for local IPC compatibility closure.

## Optional surfaces (`optional`)

- `accept4`
- `clock_nanosleep`
- `signalfd`

## Deferred surfaces (`deferred`)

The following remain deferred in v4 and are release-blocking if they stop
failing deterministically:

- `fork`
- `clone`
- `epoll`
- `io_uring`
- namespace/cgroup compatibility
- `AF_NETLINK` and raw packet socket parity

Deferred calls must preserve deterministic unsupported behavior (`-1`,
`ENOSYS`) in M36 campaign outputs.

Runtime-backed validation lane:
- `make test-real-compat-runtime-v1`
- `docs/abi/compat_runtime_corpus_v1.md`
- real ELF apps probe loader, file, socket, readiness, and explicit deferred
  syscall IDs `43`, `44`, and `45`

## Gate requirements

- Compatibility surface campaign command:
  - `python tools/run_compat_surface_campaign_v1.py --out out/compat-surface-v1.json`
- POSIX gap closure command:
  - `python tools/run_posix_gap_report_v1.py --out out/posix-gap-report-v1.json`
- Local gate: `make test-compat-surface-v1`.
- Local sub-gate: `make test-posix-gap-closure-v1`.
- CI gate: `Compatibility surface v1 gate`.
- CI sub-gate: `POSIX gap closure v1 gate`.

Gate pass requires:

- compatibility surface campaign `gate_pass = true`
- POSIX gap report `gate_pass = true`
- deferred-surface deterministic failure policy remains satisfied

## Related contracts

- `docs/runtime/syscall_coverage_matrix_v3.md`
- `docs/abi/process_model_v3.md`
- `docs/abi/socket_family_expansion_v1.md`
- `docs/abi/compat_profile_v3.md`
- `docs/abi/compat_runtime_corpus_v1.md`
