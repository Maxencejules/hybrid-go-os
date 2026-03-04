# IPv4 + UDP Profile v1

Date: 2026-03-04  
Milestone: M12 Network Stack v1

## Purpose

Define deterministic IPv4/UDP behavior required to close the M7-to-M12 gap.

## Baseline requirements

- VirtIO-net probe/init must emit deterministic readiness markers.
- ARP resolution must complete before first IPv4/UDP exchange.
- IPv4 header validation includes:
  - version/ihl checks,
  - total-length sanity checks,
  - checksum validation policy.
- UDP behavior includes:
  - deterministic receive and echo/send behavior,
  - bounded payload handling,
  - deterministic error behavior on invalid inputs.

## Marker and negative-path policy

- Positive markers:
  - `NET: virtio-net ready`
  - `NET: udp echo`
- Deterministic negative markers:
  - `NET: not found` (missing NIC profile)
  - `NET: timeout` (bounded network operation timed out)

## ABI and syscall boundary

- Raw frame path:
  - `sys_net_send`
  - `sys_net_recv`
- ABI source:
  - `docs/abi/syscall_v1.md`

## Test and gate coverage

- `tests/net/test_udp_echo.py`
- `tests/net/test_ipv4_udp_contract_v1.py`
- `tests/hw/test_hardware_matrix_v1.py`
- local/CI gate: `make test-network-stack-v1`, `Network stack v1 gate`
