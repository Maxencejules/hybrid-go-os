# SimpleFS v1 - Crash Model and Recovery Contract

Date: 2026-03-04  
Milestone: M13 Storage Reliability v1  
Status: active release gate

## Purpose

Define the storage correctness contract that upgrades `SimpleFS v0` from
functional behavior to crash-consistent behavior with deterministic recovery.

## Baseline guarantees

- Mount safety:
  - superblock and file-table structural checks run before mount success.
- Crash consistency:
  - metadata updates are committed with ordered write + replay policy.
- Recovery:
  - replay/check path restores a clean mountable state or fails
    deterministically.
- Deterministic failure behavior:
  - malformed metadata and ordering violations must not produce silent mount.

## On-disk v1 extensions over v0

- Superblock keeps v0 core fields and adds reliability metadata:
  - format version,
  - clean-shutdown flag,
  - journal/replay sequence marker.
- Metadata writes are grouped into explicit commit units.
- Recovery checks verify:
  - superblock magic and version,
  - file-table bounds,
  - replay marker consistency.

## Durability classes

- `volatile`: visible until crash; not required to survive power loss.
- `fdatasync`: payload durability class for file data writes.
- `fsync`: full durability class for data + metadata commit.

Durability classes and semantics are normatively defined in
`docs/storage/durability_model_v1.md`.

## Required tooling and tests

- Tooling:
  - `tools/storage_recover_v1.py`
  - `tools/run_storage_fault_campaign_v1.py`
- Tests:
  - `tests/storage/test_storage_contract_docs_v1.py`
  - `tests/storage/test_fsync_semantics_v1.py`
  - `tests/storage/test_write_ordering_contract_v1.py`
  - `tests/storage/test_storage_recovery_v1.py`
  - `tests/storage/test_storage_fault_campaign_v1.py`

## Required release gates

- Local: `make test-storage-reliability-v1`
- CI: `Storage reliability v1 gate`
- Artifacts:
  - `out/storage-recovery-v1.json`
  - `out/storage-fault-campaign-v1.json`
