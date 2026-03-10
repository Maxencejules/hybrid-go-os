# M44 Execution Backlog (Real Desktop + Ecosystem Qualification v2)

Date: 2026-03-09  
Lane: Rugo (Rust kernel + Go user space)  
Status: proposed

## Goal

Promote desktop/app/package claims from model-heavy simulation to runtime-backed
qualification with signed and reproducible workload evidence.

M44 source of truth remains `docs/M40_M44_GENERAL_PURPOSE_PARITY_ROADMAP.md`,
`MILESTONES.md`, and this backlog.

## Current State Summary

- Desktop v1 and ecosystem v1 gates are stable but still bounded and
  model-heavy in several campaign paths.
- Ecosystem quality and distribution workflow policies are strong, but runtime
  qualification breadth needs explicit v2 closure for stronger claims.
- M44 introduces real workload qualification and stricter release-bound
  provenance for desktop and app catalog signals.

## Execution plan

- PR-1: contract freeze
- PR-2: runtime qualification tooling + campaigns
- PR-3: release gate wiring + closure

## PR-1: Desktop/Ecosystem v2 Contract Freeze

### Objective

Define desktop profile v2 and ecosystem/distribution v2 expectations as
executable contracts.

### Scope

- Add docs:
  - `docs/desktop/desktop_profile_v2.md`
  - `docs/abi/app_compat_tiers_v2.md`
  - `docs/pkg/ecosystem_scale_policy_v2.md`
  - `docs/pkg/distribution_workflow_v2.md`
- Add tests:
  - `tests/desktop/test_desktop_docs_v2.py`
  - `tests/pkg/test_ecosystem_scale_docs_v2.py`

### Primary files

- `docs/desktop/desktop_profile_v2.md`
- `docs/abi/app_compat_tiers_v2.md`
- `docs/pkg/ecosystem_scale_policy_v2.md`
- `docs/pkg/distribution_workflow_v2.md`
- `tests/desktop/test_desktop_docs_v2.py`
- `tests/pkg/test_ecosystem_scale_docs_v2.py`

### Acceptance checks

- `python -m pytest tests/desktop/test_desktop_docs_v2.py tests/pkg/test_ecosystem_scale_docs_v2.py -v`

### Done criteria for PR-1

- Desktop/ecosystem v2 boundaries are explicit, versioned, and test-backed.
- Workload qualification thresholds are machine-verifiable.

## PR-2: Real Qualification Campaign Tooling + Tests

### Objective

Implement deterministic runtime qualification campaigns for desktop GUI and app
catalog/package workflows.

### Scope

- Add tooling:
  - `tools/run_real_gui_app_matrix_v2.py`
  - `tools/run_real_pkg_install_campaign_v2.py`
  - `tools/run_real_catalog_audit_v2.py`
- Add tests:
  - `tests/desktop/test_gui_runtime_qualification_v2.py`
  - `tests/pkg/test_pkg_install_success_rate_v2.py`
  - `tests/pkg/test_catalog_reproducibility_v2.py`
  - `tests/pkg/test_distribution_workflow_v2.py`

### Primary files

- `tools/run_real_gui_app_matrix_v2.py`
- `tools/run_real_pkg_install_campaign_v2.py`
- `tools/run_real_catalog_audit_v2.py`
- `tests/desktop/test_gui_runtime_qualification_v2.py`
- `tests/pkg/test_pkg_install_success_rate_v2.py`
- `tests/pkg/test_catalog_reproducibility_v2.py`
- `tests/pkg/test_distribution_workflow_v2.py`

### Acceptance checks

- `python tools/run_real_gui_app_matrix_v2.py --out out/real-gui-matrix-v2.json`
- `python tools/run_real_pkg_install_campaign_v2.py --out out/real-pkg-install-v2.json`
- `python tools/run_real_catalog_audit_v2.py --out out/real-catalog-audit-v2.json`
- `python -m pytest tests/desktop/test_gui_runtime_qualification_v2.py tests/pkg/test_pkg_install_success_rate_v2.py tests/pkg/test_catalog_reproducibility_v2.py tests/pkg/test_distribution_workflow_v2.py -v`

### Done criteria for PR-2

- Runtime qualification artifacts are deterministic and machine-readable.
- Desktop/app/package quality thresholds are executable and auditable.

## PR-3: Real Qualification Gate + App-Catalog Sub-gate

### Objective

Make runtime-backed desktop/ecosystem v2 qualification release-blocking.

### Scope

- Add local gates:
  - `Makefile` target `test-real-ecosystem-desktop-v2`
  - `Makefile` target `test-real-app-catalog-v2`
- Add CI steps:
  - `Real ecosystem desktop v2 gate`
  - `Real app catalog v2 gate`
- Add aggregate tests:
  - `tests/desktop/test_real_desktop_gate_v2.py`
  - `tests/pkg/test_real_catalog_gate_v2.py`

### Primary files

- `Makefile`
- `.github/workflows/ci.yml`
- `tests/desktop/test_real_desktop_gate_v2.py`
- `tests/pkg/test_real_catalog_gate_v2.py`
- `MILESTONES.md`
- `docs/STATUS.md`
- `README.md`

### Acceptance checks

- `make test-real-ecosystem-desktop-v2`
- `make test-real-app-catalog-v2`

### Done criteria for PR-3

- Real desktop/ecosystem and app-catalog sub-gates are required in local and CI
  release lanes.
- M44 can be marked done only with runtime-qualified ecosystem artifacts.

## Non-goals for M44 backlog

- Universal GUI/app compatibility claims outside declared v2 classes.
- Relaxing signed provenance and reproducibility controls for throughput.
