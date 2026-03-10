# M43 Execution Backlog (Hardware/Firmware Breadth + SMP v1)

Date: 2026-03-09  
Lane: Rugo (Rust kernel + Go user space)  
Status: proposed

## Goal

Expand release confidence from mostly virtualized profiles to broader
native-driver, firmware-table, and SMP interrupt/topology coverage.

M43 source of truth remains `docs/M40_M44_GENERAL_PURPOSE_PARITY_ROADMAP.md`,
`MILESTONES.md`, and this backlog.

## Current State Summary

- Hardware matrix v4 and promotion policy are stable, but release-blocking
  confidence remains largely QEMU profile-driven.
- Firmware hardening and measured-boot evidence exist, but broader
  firmware-table and SMP behavior needs explicit v1 closure.
- Native driver breadth (AHCI/NVMe/non-virtio NIC classes) requires stronger
  deterministic evidence before support-claim expansion.

## Execution plan

- PR-1: contract freeze
- PR-2: diagnostics and campaign implementation
- PR-3: release gate wiring + closure

## PR-1: Hardware/Firmware/SMP Contract Freeze

### Objective

Define matrix v5 and firmware/SMP baseline expectations for broader native
coverage.

### Scope

- Add docs:
  - `docs/hw/support_matrix_v5.md`
  - `docs/hw/driver_lifecycle_contract_v5.md`
  - `docs/hw/acpi_uefi_hardening_v3.md`
  - `docs/runtime/smp_interrupt_model_v1.md`
- Add tests:
  - `tests/hw/test_hw_matrix_docs_v5.py`

### Primary files

- `docs/hw/support_matrix_v5.md`
- `docs/hw/driver_lifecycle_contract_v5.md`
- `docs/hw/acpi_uefi_hardening_v3.md`
- `docs/runtime/smp_interrupt_model_v1.md`
- `tests/hw/test_hw_matrix_docs_v5.py`

### Acceptance checks

- `python -m pytest tests/hw/test_hw_matrix_docs_v5.py -v`

### Done criteria for PR-1

- Matrix v5 and firmware/SMP boundaries are explicit, versioned, and test-backed.
- Native coverage claims and unsupported boundaries are machine-verifiable.

## PR-2: Native Driver + Firmware/SMP Campaigns

### Objective

Implement deterministic matrix v5 campaigns and firmware/SMP evidence
collection for native-driver classes.

### Scope

- Add tooling:
  - `tools/run_hw_matrix_v5.py`
  - `tools/collect_firmware_smp_evidence_v1.py`
- Add tests:
  - `tests/hw/test_native_storage_driver_matrix_v1.py`
  - `tests/hw/test_native_nic_driver_matrix_v1.py`
  - `tests/hw/test_firmware_table_validation_v3.py`
  - `tests/hw/test_smp_interrupt_baseline_v1.py`

### Primary files

- `tools/run_hw_matrix_v5.py`
- `tools/collect_firmware_smp_evidence_v1.py`
- `tests/hw/test_native_storage_driver_matrix_v1.py`
- `tests/hw/test_native_nic_driver_matrix_v1.py`
- `tests/hw/test_firmware_table_validation_v3.py`
- `tests/hw/test_smp_interrupt_baseline_v1.py`

### Acceptance checks

- `python tools/run_hw_matrix_v5.py --out out/hw-matrix-v5.json`
- `python tools/collect_firmware_smp_evidence_v1.py --out out/hw-firmware-smp-v1.json`
- `python -m pytest tests/hw/test_native_storage_driver_matrix_v1.py tests/hw/test_native_nic_driver_matrix_v1.py tests/hw/test_firmware_table_validation_v3.py tests/hw/test_smp_interrupt_baseline_v1.py -v`

### Done criteria for PR-2

- Matrix/firmware/SMP artifacts are deterministic and machine-readable.
- Native-driver and topology behavior is executable and auditable.

## PR-3: Hardware/Firmware/SMP Gate + Native Driver Sub-gate

### Objective

Make expanded native driver and firmware/SMP checks release-blocking.

### Scope

- Add local gates:
  - `Makefile` target `test-hw-firmware-smp-v1`
  - `Makefile` target `test-native-driver-matrix-v1`
- Add CI steps:
  - `Hardware firmware smp v1 gate`
  - `Native driver matrix v1 gate`
- Add aggregate tests:
  - `tests/hw/test_hw_firmware_smp_gate_v1.py`
  - `tests/hw/test_native_driver_matrix_gate_v1.py`

### Primary files

- `Makefile`
- `.github/workflows/ci.yml`
- `tests/hw/test_hw_firmware_smp_gate_v1.py`
- `tests/hw/test_native_driver_matrix_gate_v1.py`
- `MILESTONES.md`
- `docs/STATUS.md`
- `README.md`

### Acceptance checks

- `make test-hw-firmware-smp-v1`
- `make test-native-driver-matrix-v1`

### Done criteria for PR-3

- Hardware/firmware/SMP and native-driver sub-gates are required in local and
  CI release lanes.
- M43 can be marked done only with deterministic matrix v5 artifacts.

## Non-goals for M43 backlog

- Broad hardware-family claims without repeatable matrix evidence.
- Promoting unsupported boards/devices to release claims without policy updates.
