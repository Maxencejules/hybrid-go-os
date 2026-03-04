# Storage Fault Campaign v1

Date: 2026-03-04  
Milestone: M13 Storage Reliability v1

## Purpose

Define deterministic storage fault injection campaigns used by the M13 gate.

## Campaign dimensions

- Fault types:
  - power-loss during data write,
  - power-loss during metadata commit,
  - superblock corruption,
  - file-table corruption.
- Workload mix:
  - metadata-heavy,
  - many-small-file,
  - large-file rewrite.
- Verification:
  - post-recovery mountability,
  - integrity check report,
  - bounded failure thresholds.

## Required report fields

- `schema: rugo.storage_fault_campaign_report.v1`
- `seed`
- `iterations`
- per-fault counters
- `total_failures`
- `max_failures`
- `meets_target`

## Gate thresholds (v1)

- deterministic campaign with fixed seed for CI.
- default `max_failures = 0`.
- threshold changes require explicit milestone-doc update.

## Evidence

- `tools/run_storage_fault_campaign_v1.py`
- `tests/storage/test_storage_fault_campaign_v1.py`
