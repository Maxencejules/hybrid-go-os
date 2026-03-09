# Driver Lifecycle Contract v4

Date: 2026-03-09  
Milestone: M37 Hardware Breadth + Driver Matrix v4  
Lane: Rugo (Rust kernel + Go user space)  
Status: active contract

## Goal

Define deterministic v4 lifecycle semantics for expanded storage/network device
classes across probe, init, runtime, recovery, and failure paths.

## Schema and report identity

Schema identifier: `rugo.driver_lifecycle_report.v4`

Required report fields:

- `driver`
- `device_class`
- `states_observed`
- `probe_attempts`
- `probe_successes`
- `init_failures`
- `runtime_errors`
- `recoveries`
- `fatal_errors`
- `status`

## Deterministic lifecycle states

| State id | Meaning | Deterministic marker expectation |
|---|---|---|
| `probe_missing` | Device class not discovered | `BLK: not found` or `NET: not found` |
| `probe_found` | Device class discovered | `BLK: found virtio-blk` or `NET: virtio-net ready` |
| `init_ready` | Driver init path complete | device-specific ready marker emitted exactly once |
| `runtime_ok` | Runtime operation succeeds | `BLK: rw ok` or `NET: udp echo` |
| `suspend_prepare` | Driver quiesce before suspend | lifecycle report state transition recorded |
| `resume_ok` | Driver restore after resume | lifecycle report state transition recorded |
| `hotplug_add` | Device add event handled | lifecycle report add event recorded |
| `hotplug_remove` | Device remove event handled | lifecycle report remove event recorded |
| `reset_recover` | Driver reset and runtime restoration | recovery event count increments |
| `error_recoverable` | Runtime error with successful recovery | recoverable error accounting increments |
| `error_fatal` | Non-recoverable error requiring escalation | gate must fail and emit reason |

## Contract rules

- Tier 0 and Tier 1 must observe `probe_found`, `init_ready`, and `runtime_ok`
  for required drivers.
- `probe_missing` markers are mandatory for negative-path checks.
- Any `error_fatal` state makes the matrix gate fail.
- Runtime errors are allowed only when paired with `error_recoverable` or
  `reset_recover` and explicit recovery accounting.
- Lifecycle claims are bounded by `docs/hw/support_matrix_v4.md`.

## Required device classes for v4 coverage

- Storage: `virtio-blk-pci`, `ahci`, `nvme`
- Network: `virtio-net-pci`, `e1000`, `rtl8139`

## Cross references

- Matrix policy: `docs/hw/support_matrix_v4.md`
- Bare-metal promotion policy: `docs/hw/bare_metal_promotion_policy_v1.md`
