# Durability Model v1

Date: 2026-03-04  
Milestone: M13 Storage Reliability v1

## Purpose

Specify durability semantics and expected crash outcomes for storage v1.

## Durability classes

- `volatile`
  - write may be visible before crash.
  - no post-crash survival guarantee.
- `fdatasync`
  - data blocks for the target file survive crash after completion.
  - metadata survival is limited to data reachability requirements.
- `fsync`
  - data and metadata for the target commit unit survive crash.
  - directory and inode metadata required for lookup is durable.

## Crash-point model

For each commit unit, crash points are modeled at:

1. before data write,
2. after data write before barrier,
3. after barrier before metadata commit,
4. after metadata commit before clean marker update,
5. after clean marker update.

Expected behavior:

- points 1-3: pre-commit state remains mountable and consistent.
- points 4-5: committed state is recoverable and mountable.

## Deterministic error requirements

- Partial commit must be detected and replayed or rejected deterministically.
- Recovery failure must return explicit failed-check evidence.
- Unsupported durability operations must fail as unsupported, never silently
  succeed.

## Evidence

- `tests/storage/test_fsync_semantics_v1.py`
- `tests/storage/test_storage_recovery_v1.py`
- `tests/storage/test_storage_fault_campaign_v1.py`
