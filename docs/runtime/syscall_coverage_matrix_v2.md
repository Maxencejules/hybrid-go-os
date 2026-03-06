# Runtime Syscall Coverage Matrix v2

Date: 2026-03-06  
Milestone: M17 Compatibility Profile v2

This matrix tracks runtime-facing syscall coverage used by compatibility profile
v2 and external app tier gates.

## Coverage matrix

| Runtime area | Syscall | ABI source | Status | Evidence | Owner | Target |
|---|---|---|---|---|---|---|
| logging | `sys_debug_write` | `syscall_v2` #0 | implemented | `tests/go/test_std_go_binary.py` | `runtime-port-owner` | M17 |
| threading | `sys_thread_spawn` | `syscall_v2` #1 | implemented | `tests/go/test_std_go_binary.py` | `runtime-port-owner` | M17 |
| threading | `sys_thread_exit` | `syscall_v2` #2 | implemented | `tests/go/test_std_go_binary.py` | `runtime-port-owner` | M17 |
| scheduling | `sys_yield` | `syscall_v2` #3 | implemented | `tests/go/test_std_go_binary.py` | `runtime-port-owner` | M17 |
| memory | `sys_vm_map` | `syscall_v2` #4 | implemented | `tests/go/test_std_go_binary.py` | `runtime-port-owner` | M17 |
| memory | `sys_vm_unmap` | `syscall_v2` #5 | implemented | `tests/go/test_std_go_binary.py` | `runtime-port-owner` | M17 |
| time | `sys_time_now` | `syscall_v2` #10 | implemented | `tests/compat/test_posix_profile_v2.py` | `compat-owner` | M17 |
| file descriptors | `sys_open` | `syscall_v2` #18 | implemented | `tests/compat/test_posix_profile_v2.py` | `compat-owner` | M17 |
| file descriptors | `sys_read` | `syscall_v2` #19 | implemented | `tests/compat/test_posix_profile_v2.py` | `compat-owner` | M17 |
| file descriptors | `sys_write` | `syscall_v2` #20 | implemented | `tests/compat/test_posix_profile_v2.py` | `compat-owner` | M17 |
| file descriptors | `sys_close` | `syscall_v2` #21 | implemented | `tests/compat/test_posix_profile_v2.py` | `compat-owner` | M17 |
| process lifecycle | `sys_wait` | `syscall_v2` #22 | implemented | `tests/compat/test_posix_profile_v2.py` | `compat-owner` | M17 |
| readiness wait | `sys_poll` | `syscall_v2` #23 | implemented | `tests/compat/test_posix_profile_v2.py` | `runtime-port-owner` | M17 |
| rights model | `sys_fd_rights_get` | `syscall_v2` #24 | implemented | `tests/compat/test_posix_profile_v2.py` | `security-owner` | M17 |
| rights model | `sys_fd_rights_reduce` | `syscall_v2` #25 | implemented | `tests/compat/test_posix_profile_v2.py` | `security-owner` | M17 |
| rights model | `sys_fd_rights_transfer` | `syscall_v2` #26 | implemented | `tests/compat/test_posix_profile_v2.py` | `security-owner` | M17 |
| security profile | `sys_sec_profile_set` | `syscall_v2` #27 | implemented | `tests/compat/test_posix_profile_v2.py` | `security-owner` | M17 |
| dynamic loader | loader relocation subset | `elf_loader_contract_v2` | implemented (bounded) | `tests/compat/test_elf_loader_dynamic_v2.py` | `compat-owner` | M17 |
| external app tier | signed package lane | `compat_profile_v2` | implemented (threshold-gated) | `tests/compat/test_external_apps_tier_v2.py` | `pkg-owner` | M17 |
| compatibility gate | `test-compat-v2` | `Makefile` | implemented | `tests/compat/test_compat_gate_v2.py` | `release-owner` | M17 |

## Explicit unsupported/runtime-deferred surfaces in v2

- `fork`/`clone` parity: deferred.
- `epoll`/`io_uring`: unsupported.
- namespace/cgroup compatibility: unsupported.
- full Linux socket-family parity (`AF_UNIX`, `AF_NETLINK`): unsupported.

Unsupported/runtime-deferred rows must remain explicit in profile docs and fail
deterministically when called.

## Update policy

Coverage changes require updates to:

- this matrix,
- `docs/abi/syscall_v2.md`,
- `docs/abi/compat_profile_v2.md`,
- `docs/abi/elf_loader_contract_v2.md`,
- `tests/compat/test_compat_gate_v2.py`.

