# SMP Interrupt Model v1

Date: 2026-03-10  
Milestone: M43 Hardware/Firmware Breadth + SMP v1  
Lane: Rugo (Rust kernel + Go user space)  
Status: active contract

## Goal

Define deterministic CPU-topology and interrupt-routing semantics for matrix v5
hardware confidence claims.

## Contract identities

- SMP interrupt model ID: `rugo.smp_interrupt_model.v1`.
- Matrix evidence schema: `rugo.hw_matrix_evidence.v5`.
- Firmware evidence schema: `rugo.hw_firmware_smp_evidence.v1`.
- Driver lifecycle schema: `rugo.driver_lifecycle_report.v5`.

## Baseline state model

| State id | Meaning | Deterministic marker expectation |
|---|---|---|
| `bootstrap_cpu_online` | BSP online and scheduler-ready | `SMP: bsp online` |
| `application_cpu_online` | AP set online and acknowledged | `SMP: ap online` |
| `irq_vector_ready` | IRQ vectors installed on active CPUs | `IRQ: vector bound` |
| `ipi_roundtrip` | Directed IPI request/ack succeeds | `SMP: ipi roundtrip ok` |
| `irq_affinity_balance` | IRQ affinity policy converges | `SMP: affinity balanced` |
| `interrupt_retarget_ok` | Interrupt retargeting succeeds under load | Lifecycle retarget counter increments without loss |

## Deterministic metric requirements

| Metric | Requirement |
|---|---|
| `bootstrap_cpu_online_ratio` | `>= 1.0` |
| `application_cpu_online_ratio` | `>= 0.99` |
| `ipi_roundtrip_p95_ms` | `<= 4.0` |
| `irq_affinity_drift` | `<= 0` |
| `lost_interrupt_events` | `<= 0` |
| `spurious_interrupt_rate` | `<= 0.01` |

## Failure policy

- Missing BSP/AP online markers fail the gate.
- Any interrupt loss or unbounded affinity drift fails the gate.
- IPI timeout or retargeting failure must emit deterministic failure reasons.

## Gate binding

- Local gate: `make test-hw-firmware-smp-v1`.
- Local sub-gate: `make test-native-driver-matrix-v1`.
- CI gate: `Hardware firmware smp v1 gate`.
- CI sub-gate: `Native driver matrix v1 gate`.

## Cross references

- Matrix policy: `docs/hw/support_matrix_v5.md`
- Firmware hardening policy: `docs/hw/acpi_uefi_hardening_v3.md`
- Driver lifecycle contract: `docs/hw/driver_lifecycle_contract_v5.md`
