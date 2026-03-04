# Bare-Metal Bring-up Runbook v1

Date: 2026-03-04  
Milestone: M9

## Goal

Provide a deterministic bring-up flow for promoting a board from exploratory
testing (Tier 2) toward supported status.

## Prerequisites

- Serial console capture available from power-on through kernel handoff.
- USB/image boot path that can load the standard Rugo ISO.
- Known-good build from current `main` branch.

## Required artifacts per run

- Board identity:
  - vendor/model
  - CPU model
  - firmware version
- Boot artifact identity:
  - commit SHA
  - ISO hash
- Serial log:
  - full raw capture
  - extracted marker summary

## Bring-up stages

### Stage 1: Boot baseline

1. Build image: `make image`
2. Boot target hardware with `out/os.iso`.
3. Capture serial output and confirm:
   - `RUGO: boot ok`
   - `RUGO: halt ok`

### Stage 2: Storage probe baseline

1. Validate a compatible storage profile for test media.
2. Run block smoke image path in controlled setup.
3. Confirm deterministic markers:
   - `BLK: found virtio-blk` (when supported profile is present)
   - or deterministic `BLK: not found` on unsupported profile

### Stage 3: Network probe baseline

1. Run network smoke image path in controlled setup.
2. Confirm deterministic markers:
   - `NET: virtio-net ready` (when supported profile is present)
   - or deterministic `NET: not found` on unsupported profile

## Promotion policy

- Tier 2 exploratory:
  - one successful run with complete evidence bundle.
- Candidate Tier 1:
  - repeated deterministic runs (minimum 5) with no regression markers.
- Release-gated tier:
  - requires automated reproducibility in CI-capable environment.

## Diagnostics checklist

- Confirm no kernel panic markers.
- Confirm probe failure paths are deterministic and explicit.
- Confirm syscall-level negative paths for DMA checks remain green:
  - `BLK: badlen ok`
  - `BLK: badptr ok`
