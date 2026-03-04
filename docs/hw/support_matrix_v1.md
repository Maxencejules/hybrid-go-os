# Hardware Support Matrix v1

Date: 2026-03-04  
Milestone: M9  
Lane: Rugo (Rust kernel + Go user space)

## Status

M9 matrix v1 is active and release-gated in CI.

## Goal

Define a tiered hardware target contract with deterministic regression signals
for boot, storage, and network bring-up.

## Tier definitions

| Tier | Target class | Contract level |
|------|--------------|----------------|
| Tier 0 | QEMU reference (`q35`) | Release-gated, must stay green |
| Tier 1 | QEMU desktop-compatible (`pc`/i440fx) | Release-gated, must stay green |
| Tier 2 | Opportunistic bare-metal boards | Manual runbook + diagnostics gate |

## Matrix targets (v1)

| Tier | Machine profile | Storage profile | Network profile | Required outcome |
|------|------------------|-----------------|-----------------|------------------|
| Tier 0 | `-machine q35` | `virtio-blk-pci` transitional | `virtio-net-pci` transitional | deterministic pass |
| Tier 1 | `-machine pc` | `virtio-blk-pci` transitional | `virtio-net-pci` transitional | deterministic pass |

## Executable conformance suite

- `tests/hw/test_hardware_matrix_v1.py`
  - storage smoke on Tier 0 and Tier 1
  - network smoke (probe + UDP echo) on Tier 0 and Tier 1
- `tests/hw/test_probe_negative_paths_v1.py`
  - deterministic missing-device probe failure markers
- `tests/hw/test_dma_safety_v1.py`
  - DMA invalid-length and invalid-pointer rejection markers

Harness fixtures are defined in `tests/conftest.py`:
- `qemu_serial_blk_q35`
- `qemu_serial_blk_i440fx`
- `qemu_serial_net_q35`
- `qemu_serial_net_i440fx`
- `qemu_serial_blk_missing`
- `qemu_serial_net_missing`

## CI gate

- Local:
  - `make test-hw-matrix`
- CI:
  - `.github/workflows/ci.yml` step: `Hardware matrix v1 gate`
  - emits `out/pytest-hw-matrix.xml` and uploads artifact `hw-matrix-junit`

## Pass/fail history policy

- Hardware matrix pass/fail history is tracked from CI runs via the uploaded
  JUnit artifact (`hw-matrix-junit`).
- M9 closure baseline: first gate-enabled run dated 2026-03-04.

## Non-goals for v1

- Full bare-metal fleet automation in CI.
- Non-virtio driver matrix expansion (NVMe/AHCI/native NIC families).
- Hotplug/reset automation beyond deterministic probe-path checks.
