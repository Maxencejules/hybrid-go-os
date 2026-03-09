# Catalog Quality Contract v1

Date: 2026-03-09  
Milestone: M39 Ecosystem Scale + Distribution Workflow v1  
Status: active release gate

## Purpose

Define deterministic quality thresholds for package installation success,
catalog metadata health, and release workflow integrity under M39.

## Contract identifiers

- Contract ID: `rugo.catalog_quality_contract.v1`.
- Parent ecosystem policy ID: `rugo.ecosystem_scale_policy.v1`.
- Install success campaign schema: `rugo.pkg_install_success_report.v1`.
- Reproducibility audit schema: `rugo.catalog_reproducibility_audit_report.v1`.

## Deterministic quality thresholds

- Stable install success ratio: `>= 0.985`.
- Canary install success ratio: `>= 0.960`.
- Edge install success ratio: `>= 0.930`.
- Stable install latency p95: `<= 75 ms`.
- Canary install latency p95: `<= 90 ms`.
- Edge install latency p95: `<= 110 ms`.
- Rollback success ratio: `>= 1.0`.
- Metadata expiry violations: `0`.
- Signature verification failures: `0`.

## Required controls

- Every release path must maintain signed provenance coverage.
- Rollback readiness must remain deterministic and release-blocking.
- Catalog metadata expiry and signature verification are release blockers.
- Any unresolved policy exception requires explicit promotion abort.

## Gate wiring

- Install success campaign runner: `tools/run_pkg_install_success_campaign_v1.py`.
- Reproducibility audit runner: `tools/run_reproducible_catalog_audit_v1.py`.
- Local gate: `make test-ecosystem-scale-v1`.
- Local sub-gate: `make test-app-catalog-health-v1`.
- CI gate: `Ecosystem scale v1 gate`.
- CI sub-gate: `App catalog health v1 gate`.

## Required tests

- `tests/pkg/test_ecosystem_scale_docs_v1.py`
- `tests/pkg/test_pkg_install_success_rate_v1.py`
- `tests/pkg/test_catalog_reproducibility_v1.py`
- `tests/pkg/test_distribution_workflow_v1.py`
- `tests/pkg/test_app_catalog_health_gate_v1.py`
