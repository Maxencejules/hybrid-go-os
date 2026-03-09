# Distribution Workflow v1

Date: 2026-03-09  
Milestone: M39 Ecosystem Scale + Distribution Workflow v1  
Status: active release gate

## Purpose

Define deterministic release distribution stages and quality controls required
for ecosystem-scale catalog operations under M39.

## Policy identity

- Policy ID: `rugo.distribution_workflow.v1`.
- Parent ecosystem policy ID: `rugo.ecosystem_scale_policy.v1`.
- Parent catalog quality contract ID: `rugo.catalog_quality_contract.v1`.
- Workflow report schema: `rugo.catalog_reproducibility_audit_report.v1`.

## Required workflow stages

- `ingest`
- `vet`
- `sign`
- `stage`
- `rollout`
- `rollback`

## Deterministic workflow thresholds

- Workflow stage completeness ratio: `>= 1.0`.
- Release signoff ratio: `>= 1.0`.
- Rollback drill pass ratio: `>= 1.0`.
- Mirror index consistency ratio: `>= 1.0`.
- Replication lag p95 minutes: `<= 15`.
- Unresolved policy exceptions: `0`.

## Gate wiring

- Workflow audit runner: `tools/run_reproducible_catalog_audit_v1.py`.
- Install quality runner: `tools/run_pkg_install_success_campaign_v1.py`.
- Local gate: `make test-ecosystem-scale-v1`.
- Local sub-gate: `make test-app-catalog-health-v1`.
- CI gate: `Ecosystem scale v1 gate`.
- CI sub-gate: `App catalog health v1 gate`.

## Failure handling

- Any failed workflow stage blocks release promotion.
- Any rollback readiness regression is release-blocking.
- Distribution claims are bounded to this workflow version.
