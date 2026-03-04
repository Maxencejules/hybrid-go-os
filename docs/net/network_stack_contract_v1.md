# Network Stack Contract v1

Date: 2026-03-04  
Milestone: M12 Network Stack v1  
Status: active release gate

## Purpose

Define the M12 network baseline as a versioned, testable contract so releases
do not rely on implicit behavior from the M7 UDP-echo path.

## Scope (v1 lane)

- L2:
  - Ethernet II framing baseline.
  - ARP for IPv4 reachability.
- L3:
  - IPv4 baseline packet handling.
  - IPv6 baseline (addressing + ND + ICMPv6 essentials).
- L4:
  - UDP deterministic send/receive behavior.
  - TCP state-machine baseline and retransmission timer policy.
- Socket semantics:
  - blocking vs non-blocking behavior.
  - poll-style readiness model and deterministic failure behavior.

## ABI boundary

- Raw frame syscalls remain part of ABI v1:
  - `sys_net_send` (`docs/abi/syscall_v1.md` #15)
  - `sys_net_recv` (`docs/abi/syscall_v1.md` #16)
- Socket behavior contract for M12 is documented in:
  - `docs/net/socket_contract_v1.md`

## Deterministic behavior requirements

- Positive path includes deterministic net-ready and UDP marker flow.
- Missing NIC path remains deterministic (`NET: not found`).
- Fault-injection and soak behavior must emit machine-readable artifacts.
- Unsupported operations fail deterministically as unsupported/invalid.

## Required release gates

- Local gate: `make test-network-stack-v1`
- CI gate: `Network stack v1 gate`
- Test suite:
  - `tests/net/test_udp_echo.py`
  - `tests/net/test_ipv4_udp_contract_v1.py`
  - `tests/net/test_tcp_state_machine_v1.py`
  - `tests/net/test_tcp_retransmission_v1.py`
  - `tests/net/test_socket_poll_semantics_v1.py`
  - `tests/net/test_ipv6_nd_icmpv6_v1.py`
  - `tests/net/test_net_interop_matrix_v1.py`
  - `tests/net/test_net_soak_v1.py`
  - `tests/net/test_socket_contract_docs_v1.py`

## Required artifacts

- `out/net-interop-v1.json`
- `out/net-soak-v1.json`
