# Hardware Support Matrix v5

Date: 2026-03-10  
Milestone: M43 Hardware/Firmware Breadth + SMP v1  
Lane: Rugo (Rust kernel + Go user space)  
Status: active contract

## Goal

Expand matrix confidence from v4 to v5 by widening native-driver breadth and
binding firmware-table plus SMP interrupt/topology behavior to deterministic
evidence.

## Tier definitions and pass criteria

| Tier | Target class | Minimum pass criteria | Gate policy |
|---|---|---|---|
| Tier 0 | QEMU reference (`q35`) | Storage/network smoke, firmware-table validation, SMP baseline checks | Release-blocking in local and CI |
| Tier 1 | QEMU compatibility (`pc`/i440fx) | Same as Tier 0 with parity and zero lifecycle regressions | Release-blocking in local and CI |
| Tier 2 | Bare-metal qualification boards | Repeated matrix v5 evidence + firmware/SMP evidence pass | Manual promotion only |
| Tier 3 | Bare-metal breadth candidates | Native driver campaign evidence and deterministic promotion staging | Never release-blocking until promoted |
| Tier 4 | Exploratory hardware profiles | Evidence-only bring-up notes | Never used for release support claims |

### Tier policy details

- Tier 0 and Tier 1 must pass `make test-hw-firmware-smp-v1` with zero failing
  tests.
- Tier 2 and Tier 3 require native driver evidence pass via
  `make test-native-driver-matrix-v1`.
- Firmware-table and SMP topology checks must produce deterministic artifacts in
  `out/hw-firmware-smp-v1.json`.
- Tier 4 remains non-claiming exploratory coverage only.

## Matrix targets (v5)

| Tier | Machine profile | Storage class set | Network class set | Firmware/table expectations | SMP expectations | Expected outcome |
|---|---|---|---|---|---|---|
| Tier 0 | `-machine q35` | `virtio-blk-pci` transitional (`disable-modern=on`) | `virtio-net-pci` transitional (`disable-modern=on`) | `RSDP`/`XSDT`/`MADT` parse and checksum pass | BSP + AP bootstrap and interrupt baseline pass | Deterministic pass |
| Tier 1 | `-machine pc` (`i440fx`) | `virtio-blk-pci` transitional (`disable-modern=on`) | `virtio-net-pci` transitional (`disable-modern=on`) | Same as Tier 0 with parity markers | Same as Tier 0 with parity markers | Deterministic pass |
| Tier 2+ evidence classes | Bare-metal campaign input | `virtio-blk-pci`, `ahci`, `nvme` | `virtio-net-pci`, `e1000`, `rtl8139` | Firmware table hardening v3 checks | Native interrupt affinity and IPI baseline checks | Policy-bounded promotion |

## Evidence artifact schema (v5)

Schema identifier: `rugo.hw_matrix_evidence.v5`

Contract identities:

- Firmware contract ID: `rugo.acpi_uefi_hardening.v3`
- SMP contract ID: `rugo.smp_interrupt_model.v1`

Required top-level fields:

- `schema`
- `created_utc`
- `matrix_contract_id`
- `driver_contract_id`
- `firmware_hardening_id`
- `smp_interrupt_model_id`
- `seed`
- `gate`
- `checks`
- `summary`
- `tier_results`
- `device_class_coverage`
- `driver_lifecycle`
- `firmware_table_validation`
- `smp_baseline`
- `native_driver_matrix`
- `artifact_refs`
- `total_failures`
- `gate_pass`
- `digest`

Required `artifact_refs` fields:

- `junit`: path to `out/pytest-hw-firmware-smp-v1.xml`
- `matrix_report`: path to `out/hw-matrix-v5.json`
- `firmware_smp_report`: path to `out/hw-firmware-smp-v1.json`
- `ci_artifact`: `hw-firmware-smp-v1-artifacts`
- `native_ci_artifact`: `native-driver-matrix-v1-artifacts`

## Executable conformance suite

- `tests/hw/test_hw_matrix_docs_v5.py`
- `tests/hw/test_native_storage_driver_matrix_v1.py`
- `tests/hw/test_native_nic_driver_matrix_v1.py`
- `tests/hw/test_firmware_table_validation_v3.py`
- `tests/hw/test_smp_interrupt_baseline_v1.py`
- `tests/hw/test_hw_firmware_smp_gate_v1.py`
- `tests/hw/test_native_driver_matrix_gate_v1.py`

## Gate binding

- Local gate: `make test-hw-firmware-smp-v1`.
- Local sub-gate: `make test-native-driver-matrix-v1`.
- CI gate: `Hardware firmware smp v1 gate`.
- CI sub-gate: `Native driver matrix v1 gate`.

## Hardware claims boundary

- Hardware support claims are bounded to matrix v5 evidence only.
- A target without current v5 matrix and firmware/SMP evidence is unsupported
  for release claims.
- Tier labels are versioned policy contracts and must be updated through v5
  docs/tests before behavior changes are accepted.
