# VirtIO Platform Profile v1

Date: 2026-03-10  
Milestone: M45 Modern Virtual Platform Parity v1  
Lane: Rugo (Rust kernel + Go user space)  
Status: shadow sub-gate contract

## Objective

Define the bounded transitional and modern VirtIO platform profiles that M45
must keep reproducible while display evidence is tied to desktop qualification.

## Profile identifiers

- VirtIO platform profile ID: `rugo.virtio_platform_profile.v1`
- Parent matrix contract: `rugo.hw.support_matrix.v6`
- Driver lifecycle contract: `rugo.driver_lifecycle_report.v6`
- Display contract: `rugo.display_stack_contract.v1`

## Required profiles

- `transitional`
  - storage device: `virtio-blk-pci,disable-modern=on`
  - network device: `virtio-net-pci,disable-modern=on`
  - transport: `pci-transitional`
  - machine coverage: `q35`, `pc/i440fx`
- `modern`
  - storage device: `virtio-blk-pci`
  - network device: `virtio-net-pci`
  - scsi device: `virtio-scsi-pci`
  - display device: `virtio-gpu-pci`
  - transport: `pci-modern`
  - machine coverage: `q35`, `pc/i440fx`

## Required evidence dimensions

- `boot_transport_class`
- `display_class`
- `desktop_display_checks`
- `virtio_profile_matrix`
- `driver_lifecycle`

## Determinism rules

- Both `transitional` and `modern` profiles must remain reproducible from a
  fixed seed.
- `desktop_display_checks` must bind the qualifying display/session checks to a
  named `display_class`.
- The default desktop qualification class for M45 is `virtio-gpu-pci`.
- Unsupported accelerated 3D or compositor claims remain out of scope for this
  profile.

## Gate binding

- Local shadow sub-gate: `make test-virtio-platform-v1`
- Local shadow gate: `make test-hw-matrix-v6`
- CI shadow sub-gate: `Virtio platform v1 shadow gate`
- CI shadow gate: `Hardware matrix v6 shadow gate`

## Promotion floor

- minimum `14` consecutive green shadow runs
- zero v5 regressions
- zero fatal lifecycle errors
- desktop display bridge checks remain green
- both `transitional` and `modern` profiles remain reproducible
