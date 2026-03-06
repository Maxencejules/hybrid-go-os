# Device Profile Contract v2

Date: 2026-03-06  
Milestone: M15  
Lane: Rugo (Rust kernel + Go user space)  
Status: active contract

## Goal

Define versioned, deterministic device-profile expectations for storage and
network targets in the M15 hardware matrix.

## Canonical profile schema

Each profile entry must declare:

- `profile_id`
- `tier`
- `machine`
- `storage_device`
- `network_device`
- `firmware_class`
- `required_markers`

Example:

```json
{
  "profile_id": "qemu.q35.virtio.v2",
  "tier": "tier0",
  "machine": "q35",
  "storage_device": "virtio-blk-pci,disable-modern=on",
  "network_device": "virtio-net-pci,disable-modern=on",
  "firmware_class": "acpi+uefi-handoff",
  "required_markers": [
    "RUGO: boot ok",
    "BLK: found virtio-blk",
    "BLK: rw ok",
    "NET: virtio-net ready",
    "NET: udp echo",
    "RUGO: halt ok"
  ]
}
```

## Deterministic lifecycle states

| State id | Meaning | Deterministic marker |
|----------|---------|----------------------|
| `probe_missing` | Device class not discovered | `BLK: not found` or `NET: not found` |
| `init_ready` | Probe + init complete | `BLK: found virtio-blk` or `NET: virtio-net ready` |
| `runtime_ok` | Runtime operation succeeds | `BLK: rw ok` or `NET: udp echo` |
| `dma_reject_badlen` | Invalid DMA length rejected | `BLK: badlen ok` |
| `dma_reject_badptr` | Invalid DMA pointer rejected | `BLK: badptr ok` |

## Contract rules

- A profile passes only if all required markers are observed.
- Negative paths must use deterministic failure markers.
- Claims are denied if marker semantics change without updating v2 docs/tests.
- Profile claims are bounded by `docs/hw/support_matrix_v2.md` tier policy.

## Cross references

- Matrix policy: `docs/hw/support_matrix_v2.md`
- DMA policy: `docs/hw/dma_iommu_strategy_v2.md`
- Firmware hardening: `docs/hw/acpi_uefi_hardening_v2.md`
