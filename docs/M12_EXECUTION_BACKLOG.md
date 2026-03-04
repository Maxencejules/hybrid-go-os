# M12 Execution Backlog (Network Stack v1)

Date: 2026-03-04  
Lane: Rugo (Rust kernel + Go user space)

## Goal

Drive M12 from the M7 UDP-echo baseline to an executable network maturity
baseline:

- publish a versioned network + socket contract,
- harden IPv4/UDP behavior and add deterministic TCP state/timer semantics,
- establish IPv6 baseline behavior (ND + ICMPv6 essentials),
- add interop and soak/fault-injection lanes with machine-readable artifacts,
- enforce a release-blocking network maturity gate in local/CI flows.

M12 source of truth remains `MILESTONES.md`, `docs/net/*`, and this backlog.

## Current State Summary

- M11 runtime/toolchain maturity v1 is complete and release-gated.
- M7 provides the current network floor: VirtIO-net + ARP + IPv4 UDP echo.
- Existing network evidence is marker-level (`tests/net/test_udp_echo.py`,
  `docs/net/udp_echo_v0.md`) and does not yet qualify as a v1 stack contract.
- ABI v1 already carries raw frame calls (`sys_net_send`, `sys_net_recv`) but
  no dedicated network stack v1 contract docs or gate exist yet.
- QEMU fixtures for network injection/matrix profiles already exist in
  `tests/conftest.py` and can be reused for M12 tests.

## Execution Result

- PR-1: complete (2026-03-04)
- PR-2: complete (2026-03-04)
- PR-3: complete (2026-03-04)

## PR-1: Contract Freeze + IPv4/UDP Baseline Gate

### Objective

Define and gate the network v1 contract before transport expansion.

### Scope

- Add contract docs:
  - `docs/net/network_stack_contract_v1.md`
  - `docs/net/socket_contract_v1.md`
  - `docs/net/ipv4_udp_profile_v1.md`
- Add/extend executable checks:
  - `tests/net/test_udp_echo.py` (positive + deterministic negative paths)
  - `tests/net/test_ipv4_udp_contract_v1.py`
  - `tests/net/test_socket_contract_docs_v1.py`
- Add optional trace helper:
  - `tools/net_trace_capture_v1.py`

### Primary files

- `docs/net/network_stack_contract_v1.md`
- `docs/net/socket_contract_v1.md`
- `docs/net/ipv4_udp_profile_v1.md`
- `tests/net/test_udp_echo.py`
- `tests/net/test_ipv4_udp_contract_v1.py`
- `tests/net/test_socket_contract_docs_v1.py`
- `tools/net_trace_capture_v1.py`
- `tests/net/test_net_trace_capture_v1.py`

### Acceptance checks

- `python -m pytest tests/net/test_udp_echo.py tests/net/test_ipv4_udp_contract_v1.py -v`
- `python -m pytest tests/net/test_socket_contract_docs_v1.py -v`

### Done criteria for PR-1

- Network/socket contracts are versioned, reviewable, and test-referenced.
- IPv4/UDP behavior (including deterministic failure paths) is executable.

## PR-2: TCP State/Timer Engine + Socket Semantics

### Objective

Add deterministic TCP baseline behavior and bind it to socket semantics.

### Scope

- Implement/test TCP baseline behavior:
  - handshake + established flow,
  - close/teardown and reset handling,
  - retransmission/timer policy with deterministic retry/fail behavior.
- Add socket semantic checks (blocking/non-blocking + poll integration).
- Add docs:
  - `docs/net/tcp_state_machine_v1.md`
  - `docs/net/retransmission_timer_policy_v1.md`

### Primary files

- `docs/net/tcp_state_machine_v1.md`
- `docs/net/retransmission_timer_policy_v1.md`
- `tests/net/v1_model.py`
- `tests/net/test_tcp_state_machine_v1.py`
- `tests/net/test_tcp_retransmission_v1.py`
- `tests/net/test_socket_poll_semantics_v1.py`

### Acceptance checks

- `python -m pytest tests/net/test_tcp_state_machine_v1.py tests/net/test_tcp_retransmission_v1.py -v`
- `python -m pytest tests/net/test_socket_poll_semantics_v1.py -v`

### Done criteria for PR-2

- TCP lifecycle/timer behavior is deterministic and test-backed.
- Socket poll/blocking semantics are documented and enforced by tests.

## PR-3: IPv6 Baseline + Interop/Soak Gate + Milestone Closure

### Objective

Close M12 with IPv6 baseline and release-blocking network maturity gates.

### Scope

- Add IPv6 baseline docs/tests:
  - `docs/net/ipv6_baseline_v1.md`
  - `tests/net/test_ipv6_nd_icmpv6_v1.py`
- Add interop + soak tooling and tests:
  - `tools/run_net_interop_matrix_v1.py`
  - `tools/run_net_soak_v1.py`
  - `tests/net/test_net_interop_matrix_v1.py`
  - `tests/net/test_net_soak_v1.py`
- Add local/CI gate wiring:
  - `Makefile` target `test-network-stack-v1`
  - `.github/workflows/ci.yml` step `Network stack v1 gate`
- Mark M12 done in milestone/status docs once gates are green.

### Primary files

- `docs/net/ipv6_baseline_v1.md`
- `tools/run_net_interop_matrix_v1.py`
- `tools/run_net_soak_v1.py`
- `tests/net/test_ipv6_nd_icmpv6_v1.py`
- `tests/net/test_net_interop_matrix_v1.py`
- `tests/net/test_net_soak_v1.py`
- `Makefile`
- `.github/workflows/ci.yml`
- `MILESTONES.md`
- `docs/STATUS.md`
- `README.md`

### Acceptance checks

- `make test-network-stack-v1`
- `python -m pytest tests/net -v`
- `python tools/run_net_interop_matrix_v1.py --out out/net-interop-v1.json`
- `python tools/run_net_soak_v1.py --out out/net-soak-v1.json`

### Done criteria for PR-3

- Network maturity gate is required in local and CI release lanes.
- Interop + soak artifacts are generated and stable for milestone evidence.
- M12 status is marked `done` with clear evidence pointers.

## Non-goals for M12 backlog

- Full Linux socket API parity.
- Advanced congestion-control variants beyond baseline policy.
- Full routing, firewall, NAT, and dynamic routing protocols.
- Broad non-virtio NIC family expansion (owned by future hardware work).
