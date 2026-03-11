# Hardware Support Matrix v2

Date: 2026-03-06  
Milestone: M15  
Lane: Rugo (Rust kernel + Go user space)  
Status: active release gate

## Goal

Define the tiered hardware confidence model that replaced the earlier
QEMU-dominant validation model, with deterministic pass criteria and evidence
artifacts.

## Tier definitions and pass criteria

| Tier | Target class | Minimum pass criteria | Gate policy |
|------|--------------|-----------------------|-------------|
| Tier 0 | QEMU reference (`q35`) | Storage smoke, network smoke, probe-negative checks, DMA rejection checks, and ACPI boot-path checks all pass | Release-blocking in local and CI |
| Tier 1 | QEMU compatibility (`pc`/i440fx) | Same checks as Tier 0, with deterministic marker parity against Tier 0 | Release-blocking in local and CI |
| Tier 2 | Bare-metal exploratory boards | Follow `docs/hw/bare_metal_bringup_v2.md` evidence bundle and pass policy | Manual promotion only |

### Tier policy details

- Tier 0 and Tier 1 must pass `make test-hw-matrix-v2` with zero failing tests.
- Tier 2 claims are evidence-only and never promoted to release claims without
  repeated deterministic passes and reviewed artifacts.

## Matrix targets (v2)

| Tier | Machine profile | Storage profile | Network profile | Expected outcome |
|------|------------------|-----------------|-----------------|------------------|
| Tier 0 | `-machine q35` | `virtio-blk-pci` transitional (`disable-modern=on`) | `virtio-net-pci` transitional (`disable-modern=on`) | Deterministic pass |
| Tier 1 | `-machine pc` (`i440fx`) | `virtio-blk-pci` transitional (`disable-modern=on`) | `virtio-net-pci` transitional (`disable-modern=on`) | Deterministic pass |

## Evidence artifact schema (v2)

Schema identifier: `rugo.hw_matrix_evidence.v2`

Required top-level fields:

- `schema`
- `generated_at_utc`
- `git_commit`
- `gate`
- `tier_results`
- `artifact_refs`

Required `tier_results[]` fields:

- `tier`
- `machine`
- `storage_smoke`
- `network_smoke`
- `probe_negative`
- `dma_policy`
- `acpi_boot_paths`
- `status`

Required `artifact_refs` fields:

- `junit`: path to `out/pytest-hw-matrix-v2.xml`
- `ci_artifact`: `hw-matrix-v2-junit`

## Executable conformance suite

- `tests/hw/test_hardware_matrix_v2.py`
- `tests/hw/test_probe_negative_paths_v2.py`
- `tests/hw/test_dma_iommu_policy_v2.py`
- `tests/hw/test_acpi_boot_paths_v2.py`
- `tests/hw/test_bare_metal_smoke_v2.py`
- `tests/hw/test_hw_gate_v2.py`

## Gate binding

- Local gate: `make test-hw-matrix-v2`
- CI gate: `.github/workflows/ci.yml` step `Hardware matrix v2 gate`
- Evidence artifact upload: `hw-matrix-v2-junit`

## Hardware claims boundary

- Hardware claims are bounded to matrix evidence only.
- Hardware support claims are bounded to matrix evidence only.
- A target without current matrix evidence is unsupported for release claims.
- Tier labels are contract versions and must be updated through v2 docs/tests.
