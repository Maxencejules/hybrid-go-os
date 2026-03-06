# Bare-Metal Bring-up Runbook v2

Date: 2026-03-06  
Milestone: M15  
Lane: Rugo (Rust kernel + Go user space)

## Goal

Provide a repeatable evidence flow for promoting boards through matrix v2
tiers without over-claiming support.

## Prerequisites

- Serial capture from power-on to halt.
- Reproducible build identity (`git` commit + ISO hash).
- Controlled media/boot path for repeated runs.

## Required evidence bundle

- `board_identity`:
  - vendor/model
  - cpu_model
  - firmware_version
- `build_identity`:
  - git_commit
  - iso_sha256
- `serial_logs`:
  - full raw log
  - marker summary
- `gate_artifacts`:
  - `out/pytest-hw-matrix-v2.xml`
  - CI artifact `hw-matrix-v2-junit`

## Bring-up stages

### Stage 1: Boot baseline

1. Build images:
   - `make image-blk`
   - `make image-net`
2. Boot and capture serial output.
3. Confirm deterministic markers:
   - `RUGO: boot ok`
   - `RUGO: halt ok`

### Stage 2: Storage and network baseline

1. Run matrix gate locally: `make test-hw-matrix-v2`
2. Confirm storage markers:
   - `BLK: found virtio-blk`
   - `BLK: rw ok`
3. Confirm network markers:
   - `NET: virtio-net ready`
   - `NET: udp echo`

### Stage 3: Negative-path and DMA baseline

Confirm deterministic rejection markers:

- `BLK: not found`
- `NET: not found`
- `BLK: badlen ok`
- `BLK: badptr ok`

## Promotion policy

- Tier 2 exploratory:
  - one complete evidence bundle with deterministic markers.
- Candidate Tier 1:
  - minimum 5 consecutive runs with no marker regressions.
- Release-claimed tier:
  - required local and CI gate pass history for matrix v2 evidence.

## Claims policy

- Hardware claims are bounded to matrix v2 artifacts only.
- Boards without current evidence remain unsupported for release claims.
