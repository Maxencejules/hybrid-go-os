# Write Ordering and Barrier Policy v1

Date: 2026-03-04  
Milestone: M13 Storage Reliability v1

## Purpose

Define required ordering between data, barriers, and metadata commits so crash
recovery remains deterministic.

## Ordering rules

For a durability-checked commit unit:

1. Write data payload blocks.
2. Issue data durability barrier/flush.
3. Write metadata updates (size, extent, allocation state).
4. Issue metadata barrier/flush.
5. Update clean commit marker.

## Forbidden ordering

- Metadata commit before durable data barrier.
- Clean marker update before metadata barrier.
- Silent reordering that changes crash outcome across identical inputs.

## Failure behavior

- Any detected ordering violation is treated as failed commit.
- Recovery path may roll forward (replay) or roll back, but outcome must be
  deterministic and reportable.

## Evidence

- `tests/storage/test_write_ordering_contract_v1.py`
- `tests/storage/test_storage_fault_campaign_v1.py`
