# M39 Execution Backlog (Ecosystem Scale + Distribution Workflow v1)

Date: 2026-03-09  
Lane: Rugo (Rust kernel + Go user space)  
Status: proposed

## Goal

Scale app/package ecosystem and distribution workflow from bounded class counts
to broader, auditable catalog operations with deterministic quality thresholds.

M39 source of truth remains `docs/M35_M39_GENERAL_PURPOSE_EXPANSION_ROADMAP.md`,
`MILESTONES.md`, and this backlog.

## Current State Summary

- Package/repo and update trust controls are mature and release-gated.
- App compatibility tiers are stable but intentionally bounded in scope and case
  counts.
- M39 introduces catalog scale policies and distribution workflow evidence gates.

## Execution Plan

- PR-1: contract freeze
- PR-2: implementation and scale simulations
- PR-3: release-gate wiring and closure

## PR-1: Ecosystem Scale Contract Freeze

### Objective

Define ecosystem and catalog quality expectations as explicit policy contracts.

### Scope

- Add docs:
  - `docs/pkg/ecosystem_scale_policy_v1.md`
  - `docs/pkg/catalog_quality_contract_v1.md`
  - `docs/pkg/distribution_workflow_v1.md`
- Add tests:
  - `tests/pkg/test_ecosystem_scale_docs_v1.py`

### Primary files

- `docs/pkg/ecosystem_scale_policy_v1.md`
- `docs/pkg/catalog_quality_contract_v1.md`
- `docs/pkg/distribution_workflow_v1.md`
- `tests/pkg/test_ecosystem_scale_docs_v1.py`

### Acceptance checks

- `python -m pytest tests/pkg/test_ecosystem_scale_docs_v1.py -v`

### Done criteria for PR-1

- Ecosystem scale and distribution contracts are explicit, versioned, and test-backed.

## PR-2: Catalog Scale Simulation + Campaigns

### Objective

Implement deterministic ecosystem-scale simulations and catalog quality checks.

### Scope

- Add tooling:
  - `tools/run_app_catalog_sim_v1.py`
  - `tools/run_pkg_install_success_campaign_v1.py`
  - `tools/run_reproducible_catalog_audit_v1.py`
- Add tests:
  - `tests/pkg/test_app_catalog_sim_v1.py`
  - `tests/pkg/test_pkg_install_success_rate_v1.py`
  - `tests/pkg/test_catalog_reproducibility_v1.py`
  - `tests/pkg/test_distribution_workflow_v1.py`

### Primary files

- `tools/run_app_catalog_sim_v1.py`
- `tools/run_pkg_install_success_campaign_v1.py`
- `tools/run_reproducible_catalog_audit_v1.py`
- `tests/pkg/test_app_catalog_sim_v1.py`
- `tests/pkg/test_pkg_install_success_rate_v1.py`
- `tests/pkg/test_catalog_reproducibility_v1.py`
- `tests/pkg/test_distribution_workflow_v1.py`

### Acceptance checks

- `python tools/run_app_catalog_sim_v1.py --out out/app-catalog-sim-v1.json`
- `python tools/run_pkg_install_success_campaign_v1.py --out out/pkg-install-success-v1.json`
- `python tools/run_reproducible_catalog_audit_v1.py --out out/catalog-audit-v1.json`
- `python -m pytest tests/pkg/test_app_catalog_sim_v1.py tests/pkg/test_pkg_install_success_rate_v1.py tests/pkg/test_catalog_reproducibility_v1.py tests/pkg/test_distribution_workflow_v1.py -v`

### Done criteria for PR-2

- Ecosystem-scale artifacts are deterministic and machine-readable.
- Catalog quality thresholds are executable and auditable.

## PR-3: Ecosystem Gate + Catalog Health Sub-gate

### Objective

Make ecosystem scale and catalog health checks release-blocking.

### Scope

- Add local gates:
  - `Makefile` target `test-ecosystem-scale-v1`
  - `Makefile` target `test-app-catalog-health-v1`
- Add CI steps:
  - `Ecosystem scale v1 gate`
  - `App catalog health v1 gate`
- Add aggregate tests:
  - `tests/pkg/test_ecosystem_scale_gate_v1.py`
  - `tests/pkg/test_app_catalog_health_gate_v1.py`

### Primary files

- `Makefile`
- `.github/workflows/ci.yml`
- `tests/pkg/test_ecosystem_scale_gate_v1.py`
- `tests/pkg/test_app_catalog_health_gate_v1.py`
- `MILESTONES.md`
- `docs/STATUS.md`
- `README.md`

### Acceptance checks

- `make test-ecosystem-scale-v1`
- `make test-app-catalog-health-v1`

### Done criteria for PR-3

- Ecosystem and catalog-health sub-gates are required in local and CI release lanes.
- M39 can be marked done with deterministic scale and quality artifacts.

## Non-goals for M39 backlog

- Immediate universal package/app compatibility across all workload classes.
- Removing signed provenance and reproducibility requirements for scale.
