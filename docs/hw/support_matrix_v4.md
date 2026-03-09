# Hardware Support Matrix v4

Date: 2026-03-09  
Milestone: M37 Hardware Breadth + Driver Matrix v4  
Lane: Rugo (Rust kernel + Go user space)  
Status: active release gate

## Goal

Expand matrix confidence from v3 to v4 by widening device-class coverage and
binding bare-metal promotion to deterministic evidence.

## Tier definitions and pass criteria

| Tier | Target class | Minimum pass criteria | Gate policy |
|---|---|---|---|
| Tier 0 | QEMU reference (`q35`) | Storage/network smoke, v4 lifecycle checks, negative-path marker checks | Release-blocking in local and CI |
| Tier 1 | QEMU compatibility (`pc`/i440fx) | Same as Tier 0 with parity and zero lifecycle regressions | Release-blocking in local and CI |
| Tier 2 | Bare-metal qualification boards | Repeated matrix v4 evidence + promotion policy pass | Manual promotion only |
| Tier 3 | Bare-metal breadth candidates | Device-class evidence collection and deterministic promotion staging | Never release-blocking until promoted |
| Tier 4 | Exploratory hardware profiles | Evidence-only bringup notes | Never used for release support claims |

### Tier policy details

- Tier 0 and Tier 1 must pass `make test-hw-matrix-v4` with zero failing tests.
- Tier 2 and Tier 3 require bare-metal promotion policy pass:
  `make test-hw-baremetal-promotion-v1`.
- Promotion thresholds are defined in
  `docs/hw/bare_metal_promotion_policy_v1.md`.
- Tier 4 remains non-claiming exploratory coverage only.

## Matrix targets (v4)

| Tier | Machine profile | Storage class set | Network class set | Expected outcome |
|---|---|---|---|---|
| Tier 0 | `-machine q35` | `virtio-blk-pci` transitional (`disable-modern=on`) | `virtio-net-pci` transitional (`disable-modern=on`) | Deterministic pass |
| Tier 1 | `-machine pc` (`i440fx`) | `virtio-blk-pci` transitional (`disable-modern=on`) | `virtio-net-pci` transitional (`disable-modern=on`) | Deterministic pass |
| Tier 2+ evidence classes | bare-metal campaign input | `virtio-blk-pci`, `ahci`, `nvme` | `virtio-net-pci`, `e1000`, `rtl8139` | Policy-bounded promotion |

## Evidence artifact schema (v4)

Schema identifier: `rugo.hw_matrix_evidence.v4`

Required top-level fields:

- `schema`
- `created_utc`
- `matrix_contract_id`
- `driver_contract_id`
- `promotion_policy_id`
- `seed`
- `gate`
- `checks`
- `summary`
- `tier_results`
- `device_class_coverage`
- `driver_lifecycle`
- `negative_paths`
- `artifact_refs`
- `total_failures`
- `gate_pass`
- `digest`

Required `artifact_refs` fields:

- `junit`: path to `out/pytest-hw-matrix-v4.xml`
- `matrix_report`: path to `out/hw-matrix-v4.json`
- `promotion_report`: path to `out/hw-promotion-v1.json`
- `ci_artifact`: `hw-matrix-v4-artifacts`
- `promotion_ci_artifact`: `hw-baremetal-promotion-v1-artifacts`

## Executable conformance suite

- `tests/hw/test_hw_matrix_docs_v4.py`
- `tests/hw/test_hw_matrix_v4.py`
- `tests/hw/test_driver_lifecycle_v4.py`
- `tests/hw/test_baremetal_promotion_v1.py`
- `tests/hw/test_hw_negative_paths_v4.py`
- `tests/hw/test_hw_gate_v4.py`
- `tests/hw/test_hw_baremetal_promotion_gate_v1.py`

## Gate binding

- Local gate: `make test-hw-matrix-v4`.
- Local sub-gate: `make test-hw-baremetal-promotion-v1`.
- CI gate: `Hardware matrix v4 gate`.
- CI sub-gate: `Hardware bare-metal promotion v1 gate`.

## Hardware claims boundary

- Hardware support claims are bounded to matrix v4 evidence only.
- A target without current v4 matrix and promotion evidence is unsupported for
  release claims.
- Tier labels are versioned policy contracts and must be updated through v4
  docs/tests before behavior changes are accepted.
