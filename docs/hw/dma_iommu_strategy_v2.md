# DMA and IOMMU Strategy v2

Date: 2026-03-06  
Milestone: M15  
Lane: Rugo (Rust kernel + Go user space)

## Scope

Define deterministic DMA safety and IOMMU policy semantics for hardware matrix
v2 targets.

## Policy goals

- Enforce fail-closed DMA behavior on invalid request shapes.
- Keep software validation mandatory on every tier, with software DMA
  validation as the baseline path.
- Expose explicit IOMMU operating mode in diagnostics.

## Deterministic DMA policy

### Request validation

- Reject non-sector-aligned block lengths (`BLK: badlen ok`).
- Reject invalid or unmapped user pointers (`BLK: badptr ok`).
- Never program a device descriptor directly from untrusted user pointers.

### Runtime behavior

- Probe/init success markers remain deterministic.
- Runtime failures must return deterministic syscall failures.
- Failures are reported without kernel panic paths.

## IOMMU mode contract

`iommu_mode` must be one of:

- `off`
- `passthrough`
- `strict`

Rules:

- `off` and `passthrough` require full software DMA validation.
- `strict` may use hardware-assisted mappings, but software checks remain
  mandatory fallback behavior.

## Stage policy

| Stage | Policy |
|-------|--------|
| Stage 0 (current gate) | software validation only, no IOMMU dependency |
| Stage 1 | detect/report IOMMU mode and keep software validation |
| Stage 2 | add explicit map/unmap domain policy with deterministic rejection |
| Stage 3 | optimize strict-mode paths without relaxing fail-closed rules |

## Executable references

- `tests/hw/test_dma_iommu_policy_v2.py`
- `tests/hw/test_probe_negative_paths_v2.py`
