# M38 Execution Backlog (Storage + Platform Feature Expansion v1)

Date: 2026-03-09  
Lane: Rugo (Rust kernel + Go user space)  
Status: proposed

## Goal

Expand platform and storage capabilities from reliability baseline to a broader
feature set with deterministic contracts and release gates.

M38 source of truth remains `docs/M35_M39_GENERAL_PURPOSE_EXPANSION_ROADMAP.md`,
`MILESTONES.md`, and this backlog.

## Current State Summary

- Storage reliability gates are mature for journaling, recovery, and power-fail
  behavior.
- Advanced storage/platform features (for example snapshots and online resize)
  were previously out of scope.
- M38 introduces feature contracts and deterministic conformance campaigns.

## Execution Plan

- PR-1: contract freeze
- PR-2: implementation and feature campaigns
- PR-3: release-gate wiring and closure

## PR-1: Storage/Platform Feature Contract Freeze

### Objective

Define advanced feature semantics as explicit contracts before implementation.

### Scope

- Add docs:
  - `docs/storage/fs_feature_contract_v1.md`
  - `docs/storage/snapshot_policy_v1.md`
  - `docs/storage/online_resize_policy_v1.md`
  - `docs/runtime/platform_feature_profile_v1.md`
- Add tests:
  - `tests/storage/test_storage_feature_docs_v1.py`

### Primary files

- `docs/storage/fs_feature_contract_v1.md`
- `docs/storage/snapshot_policy_v1.md`
- `docs/storage/online_resize_policy_v1.md`
- `docs/runtime/platform_feature_profile_v1.md`
- `tests/storage/test_storage_feature_docs_v1.py`

### Acceptance checks

- `python -m pytest tests/storage/test_storage_feature_docs_v1.py -v`

### Done criteria for PR-1

- Advanced storage/platform feature contracts are explicit and versioned.

## PR-2: Feature Campaign Tooling + Tests

### Objective

Implement deterministic feature campaigns and platform conformance checks.

### Scope

- Add tooling:
  - `tools/run_storage_feature_campaign_v1.py`
  - `tools/run_platform_feature_conformance_v1.py`
- Add tests:
  - `tests/storage/test_snapshot_semantics_v1.py`
  - `tests/storage/test_online_resize_v1.py`
  - `tests/storage/test_advanced_fs_ops_v1.py`
  - `tests/runtime/test_platform_feature_profile_v1.py`

### Primary files

- `tools/run_storage_feature_campaign_v1.py`
- `tools/run_platform_feature_conformance_v1.py`
- `tests/storage/test_snapshot_semantics_v1.py`
- `tests/storage/test_online_resize_v1.py`
- `tests/storage/test_advanced_fs_ops_v1.py`
- `tests/runtime/test_platform_feature_profile_v1.py`

### Acceptance checks

- `python tools/run_storage_feature_campaign_v1.py --out out/storage-feature-v1.json`
- `python tools/run_platform_feature_conformance_v1.py --out out/platform-feature-v1.json`
- `python -m pytest tests/storage/test_snapshot_semantics_v1.py tests/storage/test_online_resize_v1.py tests/storage/test_advanced_fs_ops_v1.py tests/runtime/test_platform_feature_profile_v1.py -v`

### Done criteria for PR-2

- Feature campaign artifacts are deterministic and machine-readable.
- Advanced feature semantics are executable and auditable.

## PR-3: Storage/Platform Gate + Feature Sub-gate

### Objective

Make advanced storage/platform feature checks release-blocking.

### Scope

- Add local gates:
  - `Makefile` target `test-storage-platform-v1`
  - `Makefile` target `test-storage-feature-contract-v1`
- Add CI steps:
  - `Storage platform v1 gate`
  - `Storage feature contract v1 gate`
- Add aggregate tests:
  - `tests/storage/test_storage_platform_gate_v1.py`
  - `tests/storage/test_storage_feature_contract_gate_v1.py`

### Primary files

- `Makefile`
- `.github/workflows/ci.yml`
- `tests/storage/test_storage_platform_gate_v1.py`
- `tests/storage/test_storage_feature_contract_gate_v1.py`
- `MILESTONES.md`
- `docs/STATUS.md`
- `README.md`

### Acceptance checks

- `make test-storage-platform-v1`
- `make test-storage-feature-contract-v1`

### Done criteria for PR-3

- Storage/platform and feature sub-gates are required in local and CI release lanes.
- M38 can be marked done with deterministic feature artifacts.

## Non-goals for M38 backlog

- Broad storage feature claims outside declared contract scope.
- Relaxing durability/recovery guarantees to add features faster.
