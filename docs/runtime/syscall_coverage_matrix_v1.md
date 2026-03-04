# Runtime Syscall Coverage Matrix v1

Date: 2026-03-04  
Milestone: M11 Runtime + Toolchain Maturity v1

This matrix tracks runtime-facing syscall behavior used by the Rugo stock-Go
lane and its near-term expansion path.

## Coverage matrix

| Runtime area | Syscall | ABI source | Status | Evidence | Owner | Target |
|---|---|---|---|---|---|---|
| logging | `sys_debug_write` | `syscall_v0` #0 | implemented | `tests/go/test_std_go_binary.py` | `runtime-port-owner` | M11 |
| threading | `sys_thread_spawn` | `syscall_v0` #1 | implemented | `tests/go/test_std_go_binary.py`, `tests/user/test_thread_spawn.py` | `runtime-port-owner` | M11 |
| threading | `sys_thread_exit` | `syscall_v0` #2 | implemented | `tests/go/test_std_go_binary.py`, `tests/user/test_thread_exit.py` | `runtime-port-owner` | M11 |
| scheduling | `sys_yield` | `syscall_v0` #3 | implemented | `tests/go/test_std_go_binary.py`, `tests/stress/test_syscall_spam.py` | `runtime-port-owner` | M11 |
| virtual memory | `sys_vm_map` | `syscall_v0` #4 | implemented | `tests/go/test_std_go_binary.py`, `tests/user/test_vm_map.py` | `runtime-port-owner` | M11 |
| virtual memory | `sys_vm_unmap` | `syscall_v0` #5 | implemented | `tests/go/test_std_go_binary.py`, `tests/user/test_vm_map.py` | `runtime-port-owner` | M11 |
| time | `sys_time_now` | `syscall_v0` #10 | implemented | `tests/go/test_std_go_binary.py` | `runtime-port-owner` | M11 |
| file descriptors | `sys_open` | `syscall_v1` #18 | implemented (compat profile baseline) | `tests/compat/test_file_io_subset.py` | `compat-owner` | M11 |
| file descriptors | `sys_read` | `syscall_v1` #19 | implemented (compat profile baseline) | `tests/compat/test_file_io_subset.py` | `compat-owner` | M11 |
| file descriptors | `sys_write` | `syscall_v1` #20 | implemented (compat profile baseline) | `tests/compat/test_file_io_subset.py` | `compat-owner` | M11 |
| file descriptors | `sys_close` | `syscall_v1` #21 | implemented (compat profile baseline) | `tests/compat/test_fd_table.py` | `compat-owner` | M11 |
| polling/netpoll basis | `sys_poll` | `syscall_v1` #23 | implemented (baseline wait primitive) | `tests/compat/test_socket_api_subset.py` | `runtime-port-owner` | M11 |
| networking runtime hooks | `sys_net_send` | `syscall_v0` #15 | deferred in runtime lane, kernel available | `tests/net/test_udp_echo.py` | `network-owner` | M12 |
| networking runtime hooks | `sys_net_recv` | `syscall_v0` #16 | deferred in runtime lane, kernel available | `tests/net/test_udp_echo.py` | `network-owner` | M12 |
| ipc/service runtime hooks | `sys_ipc_send`/`sys_ipc_recv` | `syscall_v0` #8/#9 | deferred in runtime lane, kernel available | `tests/ipc/test_ping_pong.py` | `services-owner` | M12 |

## Gap closure policy

- `implemented` rows are release-gated and must keep deterministic behavior.
- `deferred` rows must include an owner and a target milestone.
- Runtime coverage changes require updates to:
  - this matrix,
  - `docs/runtime/port_contract_v1.md`,
  - `docs/runtime/abi_stability_policy_v1.md`.
