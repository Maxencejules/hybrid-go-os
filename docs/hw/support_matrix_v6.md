# Hardware Support Matrix v6

Date: 2026-03-10  
Milestone: M45 Modern Virtual Platform Parity v1  
Lane: Rugo (Rust kernel + Go user space)  
Status: shadow gate contract

## Goal

Close the gap between the v5 transitional-VirtIO baseline and modern virtual
platform defaults while binding display-device evidence to desktop
qualification.

## Tier definitions and pass criteria

| Tier | Target class | Minimum pass criteria | Gate policy |
|---|---|---|---|
| Tier 0 | QEMU reference (`q35`) | Transitional and modern VirtIO storage/network parity, `virtio-scsi-pci`, `virtio-gpu-pci` framebuffer baseline, desktop display bridge | Shadow-gated in local and CI |
| Tier 1 | QEMU compatibility (`pc`/i440fx) | Same as Tier 0 with parity and zero lifecycle regressions | Shadow-gated in local and CI |
| Tier 2 | Bare-metal qualification boards | v5 remains the active release floor; v6 evidence may inform later promotion only | Manual promotion only |
| Tier 3 | Bare-metal breadth candidates | Evidence-only hardware expansion staging | Never release-blocking until promoted |
| Tier 4 | Exploratory hardware profiles | Bring-up notes only | Never used for release support claims |

### Tier policy details

- Tier 0 and Tier 1 must pass `make test-hw-matrix-v6` with zero failing tests.
- VirtIO platform profile conformance must pass
  `make test-virtio-platform-v1`.
- v5 remains the active release-blocking floor through
  `make test-hw-firmware-smp-v1` until v6 promotion criteria are met.
- Promotion from shadow gate to active contract requires:
  - minimum `14` consecutive green shadow runs,
  - zero v5 regressions,
  - zero fatal lifecycle errors,
  - desktop display bridge checks remain green,
  - both transitional and modern VirtIO profiles remain reproducible.

## Matrix targets (v6)

| Tier | Machine profile | Transitional classes | Modern classes | Extended classes | Display bridge expectation | Expected outcome |
|---|---|---|---|---|---|---|
| Tier 0 | `-machine q35` | `virtio-blk-pci` + `virtio-net-pci` with `disable-modern=on` | `virtio-blk-pci` + `virtio-net-pci` | `virtio-scsi-pci`, `virtio-gpu-pci` | Desktop smoke names the display class and keeps `desktop_display_checks` green | Deterministic shadow pass |
| Tier 1 | `-machine pc` (`i440fx`) | same as Tier 0 | same as Tier 0 | same as Tier 0 | same as Tier 0 with parity markers | Deterministic shadow pass |
| Tier 2+ evidence classes | Bare-metal campaign input | v5-bound release floor remains active | Modern VirtIO evidence only | future M46/M47 promotion input | no claim broadening from display markers alone | Policy-bounded evidence |

## Evidence artifact schema (v6)

Schema identifier: `rugo.hw_matrix_evidence.v6`

Contract identities:

- Driver contract ID: `rugo.driver_lifecycle_report.v6`
- VirtIO platform profile ID: `rugo.virtio_platform_profile.v1`
- Display contract ID: `rugo.display_stack_contract.v1`
- Shadow baseline contract ID: `rugo.hw.support_matrix.v5`

Required top-level fields:

- `schema`
- `created_utc`
- `matrix_contract_id`
- `driver_contract_id`
- `virtio_platform_profile_id`
- `display_contract_id`
- `shadow_baseline_contract_id`
- `seed`
- `gate`
- `checks`
- `summary`
- `tier_results`
- `virtio_profile_matrix`
- `device_class_coverage`
- `driver_lifecycle`
- `boot_transport_class`
- `display_class`
- `desktop_display_checks`
- `negative_paths`
- `shadow_gate`
- `artifact_refs`
- `total_failures`
- `gate_pass`
- `digest`

Required `artifact_refs` fields:

- `junit`: path to `out/pytest-hw-matrix-v6.xml`
- `matrix_report`: path to `out/hw-matrix-v6.json`
- `desktop_smoke_report`: path to `out/desktop-smoke-v1.json`
- `ci_artifact`: `hw-matrix-v6-artifacts`
- `platform_ci_artifact`: `virtio-platform-v1-artifacts`
- `shadow_baseline_artifact`: `hw-firmware-smp-v1-artifacts`

## Executable conformance suite

- `tests/hw/test_hw_matrix_docs_v6.py`
- `tests/hw/test_virtio_platform_profile_v1.py`
- `tests/hw/test_virtio_modern_storage_v1.py`
- `tests/hw/test_virtio_modern_net_v1.py`
- `tests/hw/test_virtio_scsi_v1.py`
- `tests/hw/test_virtio_gpu_framebuffer_v1.py`
- `tests/hw/test_driver_lifecycle_v6.py`
- `tests/hw/test_hw_negative_paths_v5.py`
- `tests/desktop/test_display_device_bridge_v1.py`
- `tests/hw/test_hw_gate_v6.py`
- `tests/hw/test_virtio_platform_gate_v1.py`

## Gate binding

- Local gate: `make test-hw-matrix-v6`.
- Local sub-gate: `make test-virtio-platform-v1`.
- CI gate: `Hardware matrix v6 shadow gate`.
- CI sub-gate: `Virtio platform v1 shadow gate`.

## Hardware claims boundary

- v6 is an evidence-only shadow contract until promotion criteria are met.
- Display-device qualification claims require a non-empty `display_class` and a
  passing `desktop_display_checks` section.
- Modern VirtIO classes and `virtio-gpu-pci` are contract surfaces, not implied
  support claims.
- No support claim broadens until the shadow promotion criteria are satisfied.
