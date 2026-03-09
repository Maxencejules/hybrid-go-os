# M20 Execution Backlog (Operability + Release UX v2)

Date: 2026-03-06  
Lane: Rugo (Rust kernel + Go user space)  
Status: done

## Goal

Close the gap between engineering milestone closure and day-to-day operational
quality: installer, upgrade, rollback, recovery, and supportability.

M20 source of truth remains `docs/M15_M20_MULTIPURPOSE_PLAN.md`,
`MILESTONES.md`, and this backlog.

## Current State Summary

- M14 established productization/release-engineering v1 baseline.
- M15-M19 define hardware/process/compat/storage/network v2 work.
- M20 is the integrator milestone that makes release operations routine.

## Execution Result

- PR-1: complete (2026-03-09)
- PR-2: complete (2026-03-09)
- PR-3: complete (2026-03-09)

## PR-1: Installer + Operational Contract v2

### Objective

Define install and recovery baseline as executable contracts.

### Scope

- Add docs:
  - `docs/build/installer_recovery_baseline_v2.md`
  - `docs/build/operations_runbook_v2.md`
- Add tooling:
  - `tools/build_installer_v2.py`
- Add tests:
  - `tests/build/test_installer_recovery_v2.py`

### Primary files

- `docs/build/installer_recovery_baseline_v2.md`
- `docs/build/operations_runbook_v2.md`
- `tools/build_installer_v2.py`
- `tests/build/test_installer_recovery_v2.py`

### Acceptance checks

- `python tools/build_installer_v2.py --out out/installer-v2.json`
- `python -m pytest tests/build/test_installer_recovery_v2.py -v`

### Done criteria for PR-1

- Installer/recovery contracts are versioned and executable-check referenced.
- Operator baseline expectations are explicit and reviewable.

### PR-1 completion summary

- Added installer and operations contracts:
  - `docs/build/installer_recovery_baseline_v2.md`
  - `docs/build/operations_runbook_v2.md`
- Added deterministic installer artifact generator:
  - `tools/build_installer_v2.py`
- Added executable installer/recovery contract checks:
  - `tests/build/test_installer_recovery_v2.py`

## PR-2: Upgrade + Rollback Drills v2

### Objective

Validate deterministic upgrade, rollback, and support-bundle workflows.

### Scope

- Add docs:
  - `docs/pkg/update_protocol_v2.md`
  - `docs/pkg/rollback_policy_v2.md`
- Add tooling:
  - `tools/run_upgrade_recovery_drill_v2.py`
  - `tools/collect_support_bundle_v2.py`
- Add tests:
  - `tests/build/test_upgrade_rollback_v2.py`
  - `tests/build/test_support_bundle_v2.py`

### Primary files

- `docs/pkg/update_protocol_v2.md`
- `docs/pkg/rollback_policy_v2.md`
- `tools/run_upgrade_recovery_drill_v2.py`
- `tools/collect_support_bundle_v2.py`
- `tests/build/test_upgrade_rollback_v2.py`
- `tests/build/test_support_bundle_v2.py`

### Acceptance checks

- `python tools/run_upgrade_recovery_drill_v2.py --out out/upgrade-recovery-v2.json`
- `python tools/collect_support_bundle_v2.py --out out/support-bundle-v2.json`
- `python -m pytest tests/build/test_upgrade_rollback_v2.py tests/build/test_support_bundle_v2.py -v`

### Done criteria for PR-2

- Upgrade/rollback/support bundle workflows are deterministic and auditable.
- Artifact schemas are stable and machine-readable.

### PR-2 completion summary

- Added upgrade and rollback policy docs:
  - `docs/pkg/update_protocol_v2.md`
  - `docs/pkg/rollback_policy_v2.md`
- Added deterministic drill and support-bundle tooling:
  - `tools/run_upgrade_recovery_drill_v2.py`
  - `tools/collect_support_bundle_v2.py`
- Added executable checks for drill and bundle schemas:
  - `tests/build/test_upgrade_rollback_v2.py`
  - `tests/build/test_support_bundle_v2.py`

## PR-3: Operability Gate + Milestone Closure

### Objective

Promote operability/release UX v2 checks to required release gates.

### Scope

- Add aggregate test:
  - `tests/build/test_operability_gate_v2.py`
- Add local gate:
  - `Makefile` target `test-release-ops-v2`
- Add CI gate:
  - `.github/workflows/ci.yml` step `Operability and release UX v2 gate`
- Mark closure docs after green gate:
  - `MILESTONES.md`
  - `docs/STATUS.md`
  - `README.md`

### Primary files

- `tests/build/test_operability_gate_v2.py`
- `Makefile`
- `.github/workflows/ci.yml`
- `MILESTONES.md`
- `docs/STATUS.md`
- `README.md`

### Acceptance checks

- `make test-release-ops-v2`

### Done criteria for PR-3

- Operability v2 gate is required in local and CI release lanes.
- M20 can be marked done with evidence-linked artifacts.

### PR-3 completion summary

- Added aggregate gate test:
  - `tests/build/test_operability_gate_v2.py`
- Added local gate:
  - `make test-release-ops-v2`
  - JUnit output: `out/pytest-release-ops-v2.xml`
- Added CI gate + artifact upload:
  - step: `Operability and release UX v2 gate`
  - artifact: `release-ops-v2-artifacts`
- Updated closure docs:
  - `MILESTONES.md`
  - `docs/STATUS.md`
  - `README.md`

## Non-goals for M20 backlog

- Broad desktop UX scope beyond operability baselines.
- Full enterprise control-plane features (fleet orchestration belongs later).
