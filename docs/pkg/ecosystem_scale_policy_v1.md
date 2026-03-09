# Ecosystem Scale Policy v1

Date: 2026-03-09  
Milestone: M39 Ecosystem Scale + Distribution Workflow v1  
Status: active release gate

## Purpose

Define bounded, deterministic ecosystem-scale thresholds for app/package
catalog growth under M39.

## Contract identifiers

- Policy ID: `rugo.ecosystem_scale_policy.v1`.
- Catalog quality contract ID: `rugo.catalog_quality_contract.v1`.
- Distribution workflow ID: `rugo.distribution_workflow.v1`.
- App catalog simulation schema: `rugo.app_catalog_sim_report.v1`.
- Install success campaign schema: `rugo.pkg_install_success_report.v1`.
- Reproducibility audit schema: `rugo.catalog_reproducibility_audit_report.v1`.

## Required scale thresholds

- Total catalog entries: `>= 420`.
- Class coverage floor per declared class: `>= 70`.
- Catalog metadata completeness ratio: `>= 0.995`.
- Signed provenance coverage ratio: `>= 1.0`.
- Unsupported workload ratio: `<= 0.02`.
- Policy violation count: `0`.

## Class coverage floors

- `productivity`: `>= 120` entries.
- `devtools`: `>= 90` entries.
- `media`: `>= 70` entries.
- `utility`: `>= 140` entries.

## Gate wiring

- App catalog simulator: `tools/run_app_catalog_sim_v1.py`.
- Install-success campaign: `tools/run_pkg_install_success_campaign_v1.py`.
- Reproducibility audit: `tools/run_reproducible_catalog_audit_v1.py`.
- Local gate: `make test-ecosystem-scale-v1`.
- Local sub-gate: `make test-app-catalog-health-v1`.
- CI gate: `Ecosystem scale v1 gate`.
- CI sub-gate: `App catalog health v1 gate`.

## Evidence artifacts

- `out/app-catalog-sim-v1.json`
- `out/pkg-install-success-v1.json`
- `out/catalog-audit-v1.json`
- `out/pytest-ecosystem-scale-v1.xml`
- `out/pytest-app-catalog-health-v1.xml`

## Policy boundary

- M39 claims are limited to declared thresholds and declared workload classes.
- Additional catalog classes require explicit contract version updates.
