# DMA Safety and IOMMU Strategy v1

Date: 2026-03-04  
Milestone: M9

## Scope

Define the current DMA safety contract and the staged IOMMU adoption plan for
Rugo x86_64 hardware enablement.

## Current DMA safety contract (implemented)

### Copy-in/copy-out boundary

- User buffers are never programmed directly into device descriptors.
- Syscall paths copy through kernel-owned buffers before and after DMA:
  - block read: device -> kernel page -> validated user copyout
  - block write: validated user copyin -> kernel page -> device

### User pointer validation

- User memory ranges are rejected on:
  - invalid range/overflow,
  - unmapped pages,
  - missing required permissions.

### Deterministic failure behavior

- Invalid DMA request shape must return deterministic syscall failure.
- Invalid user pointer mapping must return deterministic syscall failure.

## Executable checks

- `tests/hw/test_dma_safety_v1.py`
  - `BLK: badlen ok` (`sys_blk_read` rejects non-sector-aligned length)
  - `BLK: badptr ok` (`sys_blk_read` rejects unmapped user pointer)
- Existing M5 driver checks continue to validate the baseline:
  - `tests/drivers/test_virtio_blk_badlen.py`
  - `tests/drivers/test_virtio_blk_badptr.py`

## IOMMU strategy (staged)

### Stage 0 (current)

- No IOMMU dependency in release gate.
- Enforce strict software DMA bounds and user-pointer isolation.

### Stage 1

- Introduce IOMMU capability detection and explicit mode reporting.
- Keep software validation as mandatory fallback.

### Stage 2

- Introduce per-device DMA domains and map/unmap API.
- Reject mappings that exceed driver-declared window constraints.

### Stage 3

- Move hot paths to IOMMU-backed mappings where available.
- Keep deterministic software fallback for unsupported hardware tiers.

## Non-goals for v1

- Full VT-d/AMD-Vi implementation.
- Per-process DMA isolation.
- Device passthrough support.
