# M13 Execution Backlog (Storage Reliability v1)

Date: 2026-03-04  
Lane: Rugo (Rust kernel + Go user space)

## Goal

Drive M13 from the current `SimpleFS v0` baseline to an executable storage
reliability baseline:

- publish versioned crash-consistency and durability contracts,
- define deterministic write-ordering/barrier semantics,
- add replay/recovery and integrity tooling with machine-readable reports,
- run power-loss/corruption campaigns with deterministic outcomes,
- enforce a release-blocking storage reliability gate in local/CI flows.

M13 source of truth remains `MILESTONES.md`, `docs/storage/*`, and this
backlog.

## Current State Summary

- M12 network stack v1 is complete and release-gated.
- M6 provides functional filesystem behavior and package/app flow.
- Current filesystem contract is `SimpleFS v0` (`docs/storage/fs_v0.md`).
- Deterministic image build path already exists (`tools/mkfs.py`).
- Existing storage tests cover mount baseline and bad-magic rejection:
  - `tests/fs/test_fsd_smoke.py`
  - `tests/fs/test_fsd_bad_magic.py`
- Missing for M13 closure: storage v1 crash/durability contract, recovery
  tooling, power-loss/corruption campaigns, and dedicated storage CI gate.

## Execution Result

- PR-1: complete (2026-03-04)
- PR-2: complete (2026-03-04)
- PR-3: complete (2026-03-04)

## PR-1: Storage Contract Freeze + Crash Model Baseline

### Objective

Define storage v1 guarantees and make durability semantics executable before
recovery implementation lands.

### Scope

- Add storage contract docs:
  - `docs/storage/fs_v1.md`
  - `docs/storage/durability_model_v1.md`
  - `docs/storage/write_ordering_policy_v1.md`
- Add contract tests:
  - `tests/storage/test_storage_contract_docs_v1.py`
  - `tests/storage/test_fsync_semantics_v1.py`
  - `tests/storage/test_write_ordering_contract_v1.py`
- Record explicit deferred items with owner/target date where applicable.

### Primary files

- `docs/storage/fs_v1.md`
- `docs/storage/durability_model_v1.md`
- `docs/storage/write_ordering_policy_v1.md`
- `tests/storage/test_storage_contract_docs_v1.py`
- `tests/storage/test_fsync_semantics_v1.py`
- `tests/storage/test_write_ordering_contract_v1.py`
- `tests/storage/v1_model.py`

### Acceptance checks

- `python -m pytest tests/storage/test_storage_contract_docs_v1.py -v`
- `python -m pytest tests/storage/test_fsync_semantics_v1.py tests/storage/test_write_ordering_contract_v1.py -v`

### Done criteria for PR-1

- Storage v1 contracts are versioned, reviewable, and test-referenced.
- Crash/durability semantics have no unowned placeholders.

## PR-2: Replay/Recovery Tooling + Fault-Campaign Harness

### Objective

Implement deterministic recovery behavior and validate it against corruption and
power-loss scenarios.

### Scope

- Add recovery/fault tooling:
  - `tools/storage_recover_v1.py`
  - `tools/run_storage_fault_campaign_v1.py`
- Add executable checks:
  - `tests/storage/test_storage_recovery_v1.py`
  - `tests/storage/test_storage_fault_campaign_v1.py`
  - `tests/storage/test_storage_integrity_checker_v1.py`
- Add docs:
  - `docs/storage/recovery_playbook_v1.md`
  - `docs/storage/fault_campaign_v1.md`

### Primary files

- `tools/storage_recover_v1.py`
- `tools/run_storage_fault_campaign_v1.py`
- `tests/storage/test_storage_recovery_v1.py`
- `tests/storage/test_storage_fault_campaign_v1.py`
- `tests/storage/test_storage_integrity_checker_v1.py`
- `docs/storage/recovery_playbook_v1.md`
- `docs/storage/fault_campaign_v1.md`

### Acceptance checks

- `python tools/storage_recover_v1.py --check --out out/storage-recovery-v1.json`
- `python tools/run_storage_fault_campaign_v1.py --seed 20260304 --out out/storage-fault-campaign-v1.json`
- `python -m pytest tests/storage/test_storage_recovery_v1.py tests/storage/test_storage_fault_campaign_v1.py -v`

### Done criteria for PR-2

- Recovery and fault-campaign tools emit stable machine-readable artifacts.
- Corruption/power-loss scenarios have deterministic pass/fail outcomes.

## PR-3: Storage Reliability Gate + Milestone Closure

### Objective

Promote M13 reliability checks to release-blocking gates and close milestone
status docs with evidence pointers.

### Scope

- Add local gate:
  - `Makefile` target `test-storage-reliability-v1`
- Add CI gate:
  - `.github/workflows/ci.yml` step `Storage reliability v1 gate`
- Add aggregate gate test:
  - `tests/storage/test_storage_reliability_gate_v1.py`
- Wire gate artifacts:
  - `out/storage-recovery-v1.json`
  - `out/storage-fault-campaign-v1.json`
- Mark M13 done in milestone/status docs once gate is green.

### Primary files

- `Makefile`
- `.github/workflows/ci.yml`
- `tests/storage/test_storage_reliability_gate_v1.py`
- `MILESTONES.md`
- `docs/STATUS.md`
- `README.md`
- `docs/POST_G2_EXTENDED_MILESTONES.md`

### Acceptance checks

- `make test-storage-reliability-v1`
- `python -m pytest tests/storage -v`
- `python tools/storage_recover_v1.py --check --out out/storage-recovery-v1.json`
- `python tools/run_storage_fault_campaign_v1.py --seed 20260304 --out out/storage-fault-campaign-v1.json`

### Done criteria for PR-3

- Storage reliability gate is required in local and CI release lanes.
- Recovery/fault artifacts are generated and stable for milestone evidence.
- M13 status is marked `done` with clear evidence pointers.

## Non-goals for M13 backlog

- Full production filesystem feature parity (quotas, online resize, snapshots).
- Complete CoW snapshot/rollback subsystem unless explicitly selected.
- Broad storage hardware-family expansion beyond current virtio baseline.
