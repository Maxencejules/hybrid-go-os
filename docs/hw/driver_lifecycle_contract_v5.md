# Driver Lifecycle Contract v5

Date: 2026-03-10  
Milestone: M43 Hardware/Firmware Breadth + SMP v1  
Lane: Rugo (Rust kernel + Go user space)  
Status: active contract

## Goal

Define deterministic v5 lifecycle semantics for native storage/network drivers
plus SMP interrupt behavior across probe, init, runtime, recovery, and failure
paths.

## Schema and report identity

Schema identifier: `rugo.driver_lifecycle_report.v5`

Required report fields:

- `driver`
- `device_class`
- `states_observed`
- `probe_attempts`
- `probe_successes`
- `init_failures`
- `runtime_errors`
- `irq_retarget_events`
- `affinity_balance_events`
- `recoveries`
- `fatal_errors`
- `status`

## Deterministic lifecycle states

| State id | Meaning | Deterministic marker expectation |
|---|---|---|
| `probe_missing` | Device class not discovered | `BLK: not found` or `NET: not found` |
| `probe_found` | Device class discovered | `BLK: found virtio-blk` or `NET: virtio-net ready` |
| `init_ready` | Driver init path complete | Device-specific ready marker emitted exactly once |
| `runtime_ok` | Runtime operation succeeds | `BLK: rw ok` or `NET: udp echo` |
| `irq_vector_bound` | IRQ vector bind completed | `IRQ: vector bound` |
| `irq_vector_retarget` | IRQ moved across CPUs under policy | Lifecycle report retarget counter increments |
| `cpu_affinity_balance` | IRQ affinity stays policy-balanced | `SMP: affinity balanced` |
| `reset_recover` | Driver reset and runtime restoration | Recovery event count increments |
| `error_recoverable` | Runtime error with successful recovery | Recoverable error accounting increments |
| `error_fatal` | Non-recoverable error requiring escalation | Gate must fail and emit reason |

## Contract rules

- Tier 0 and Tier 1 must observe `probe_found`, `init_ready`, `runtime_ok`, and
  `irq_vector_bound` for required drivers.
- Native campaign classes must additionally observe `irq_vector_retarget` and
  `cpu_affinity_balance` without fatal errors.
- `probe_missing` markers are mandatory for negative-path checks.
- Any `error_fatal` state makes the matrix gate fail.
- Runtime errors are allowed only when paired with `error_recoverable` or
  `reset_recover` and explicit recovery accounting.
- Lifecycle claims are bounded by `docs/hw/support_matrix_v5.md`.

## Required device classes for v5 coverage

- Storage: `virtio-blk-pci`, `ahci`, `nvme`
- Network: `virtio-net-pci`, `e1000`, `rtl8139`

## Cross references

- Matrix policy: `docs/hw/support_matrix_v5.md`
- Firmware hardening policy: `docs/hw/acpi_uefi_hardening_v3.md`
- SMP interrupt model: `docs/runtime/smp_interrupt_model_v1.md`
