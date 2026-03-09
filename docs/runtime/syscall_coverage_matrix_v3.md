# Runtime Syscall Coverage Matrix v3

Date: 2026-03-09  
Milestone: M36 Compatibility Surface Expansion v1

This matrix tracks compatibility-surface expansion commitments introduced for
`compat_profile_v4`.

## Coverage matrix

| Surface area | API / syscall | Contract source | Status | Evidence | Owner | Target |
|---|---|---|---|---|---|---|
| process lifecycle | `waitid` | `process_model_v3` | implemented | `tests/compat/test_process_model_v3.py` | `compat-owner` | M36 |
| process signaling | `sigprocmask` | `process_model_v3` | implemented | `tests/compat/test_process_model_v3.py` | `compat-owner` | M36 |
| process signaling | `sigpending` | `process_model_v3` | implemented | `tests/compat/test_process_model_v3.py` | `compat-owner` | M36 |
| readiness wait | `pselect` | `compat_profile_v4` | implemented | `tests/compat/test_posix_gap_closure_v1.py` | `runtime-port-owner` | M36 |
| readiness wait | `ppoll` | `compat_profile_v4` | implemented | `tests/compat/test_posix_gap_closure_v1.py` | `runtime-port-owner` | M36 |
| socket messaging | `sendmsg` | `socket_family_expansion_v1` | implemented | `tests/compat/test_socket_family_expansion_v1.py` | `net-owner` | M36 |
| socket messaging | `recvmsg` | `socket_family_expansion_v1` | implemented | `tests/compat/test_socket_family_expansion_v1.py` | `net-owner` | M36 |
| local sockets | `socketpair` | `socket_family_expansion_v1` | implemented | `tests/compat/test_socket_family_expansion_v1.py` | `net-owner` | M36 |
| socket families | `AF_INET` / `AF_INET6` | `socket_family_expansion_v1` | implemented | `tests/compat/test_socket_family_expansion_v1.py` | `net-owner` | M36 |
| socket families | `AF_UNIX` subset | `socket_family_expansion_v1` | implemented (bounded) | `tests/compat/test_socket_family_expansion_v1.py` | `net-owner` | M36 |
| deferred process parity | `fork`, `clone` | `compat_profile_v4` | deferred, deterministic `ENOSYS` | `tests/compat/test_deferred_surface_behavior_v1.py` | `compat-owner` | M36 |
| deferred readiness APIs | `epoll`, `io_uring` | `compat_profile_v4` | deferred, deterministic `ENOSYS` | `tests/compat/test_deferred_surface_behavior_v1.py` | `compat-owner` | M36 |
| deferred containment | namespace/cgroup compatibility | `compat_profile_v4` | deferred, deterministic `ENOSYS` | `tests/compat/test_deferred_surface_behavior_v1.py` | `compat-owner` | M36 |
| deferred socket families | `AF_NETLINK` / raw packet parity | `socket_family_expansion_v1` | deferred, deterministic `ENOSYS` | `tests/compat/test_deferred_surface_behavior_v1.py` | `net-owner` | M36 |
| compatibility surface gate | `test-compat-surface-v1` | `Makefile` | implemented | `tests/compat/test_compat_surface_gate_v1.py` | `release-owner` | M36 |
| posix sub-gate | `test-posix-gap-closure-v1` | `Makefile` | implemented | `tests/compat/test_posix_gap_closure_gate_v1.py` | `release-owner` | M36 |

## Deterministic deferred-surface policy

Rows marked `deferred` are not latent support claims. M36 policy requires the
same deterministic unsupported behavior for every run:

- syscall/API returns `-1`
- deterministic error contract is `ENOSYS`
- report rows remain stable and machine-readable

## Update policy

Coverage changes require updates to:

- this matrix
- `docs/abi/compat_profile_v4.md`
- `docs/abi/process_model_v3.md`
- `docs/abi/socket_family_expansion_v1.md`
- `tests/compat/test_compat_surface_gate_v1.py`
- `tests/compat/test_posix_gap_closure_gate_v1.py`
