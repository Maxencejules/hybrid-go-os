# Compatibility Profile v1

## Lane

Rugo (Rust kernel + Go user space).

## Status

Draft profile established in M8 PR-1 on 2026-03-04. This document defines the
target surface that M8 PR-2/PR-3 must implement and gate in CI.

## Goal

Provide a stable, POSIX-oriented subset that can run meaningful third-party
CLI/service workloads in the Rugo QEMU reference environment.

This is explicitly a subset profile, not full POSIX or full Linux ABI
compatibility.

## Profile classes

- `required`: must be implemented for Compatibility Profile v1 conformance.
- `optional`: may be absent in v1; absence must fail deterministically.
- `unsupported`: explicitly out of scope for v1.

## Required POSIX-oriented API subset

### Process lifecycle subset (`required`)

- `execve`-style user program entry with deterministic `argv`/`envp` delivery.
- `_exit`/`exit` semantics with stable status propagation.
- `wait`/`waitpid` direct-child wait semantics.
- Stable process identity basics (`getpid` at minimum).

Conformance skeleton: `tests/compat/test_process_lifecycle.py`.

### File I/O subset (`required`)

- `open`/`openat`, `read`, `write`, `close`.
- `lseek` and deterministic offset behavior.
- `fstat`/`stat` minimum metadata query behavior.
- Deterministic file descriptor table behavior for invalid/closed descriptors.

Conformance skeleton: `tests/compat/test_file_io_subset.py`.

### Time and signal subset (`required`)

- `clock_gettime` baseline for monotonic and realtime clocks.
- `nanosleep` baseline semantics.
- Minimal signal handling (`sigaction`, `kill`) for selected signals.
- Deterministic interruption/restart behavior where documented.

Conformance skeleton: `tests/compat/test_time_signal_subset.py`.

### Socket API subset (`required`)

- `socket`, `bind`, `listen`, `accept`, `connect`.
- `send`/`recv` and `sendto`/`recvfrom` baseline behavior.
- `shutdown` baseline behavior.
- `poll` or equivalent readiness wait primitive baseline.

Conformance skeleton: `tests/compat/test_socket_api_subset.py`.

## Explicit unsupported list for v1

The following are explicitly not part of Compatibility Profile v1:

- Full Linux syscall ABI emulation.
- `fork`/`vfork`/`clone` compatibility surface.
- `ptrace`, seccomp-BPF compatibility, and namespaces/cgroups compatibility.
- `epoll`, `io_uring`, `inotify`, `fanotify`, `eventfd`, `signalfd`, `timerfd`.
- `AF_UNIX`, `AF_NETLINK`, and raw packet sockets.
- PTY/job-control/terminal stack parity with Linux.
- Full POSIX option groups beyond the required subset above.

Unsupported APIs must fail deterministically as unsupported and must not be
silently mapped to partial behavior.

## Conformance and CI intent

- Profile conformance is tracked by `tests/compat/`.
- M8 PR-1 delivers deterministic skeleton tests with TODO markers.
- M8 PR-2/PR-3 will replace skeleton TODOs with executable behavior checks and
  promote them to release-gating CI.

## Relationship to syscall contract

Syscall-level compatibility, versioning, error model, and deprecation policy
are defined in `docs/abi/syscall_v1.md`.
