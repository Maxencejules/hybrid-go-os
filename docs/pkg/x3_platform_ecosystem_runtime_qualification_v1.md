# X3 Platform And Ecosystem Runtime Qualification v1

Date: 2026-03-18  
Track: X3 Platform and Ecosystem Feature Breadth  
Lane: Rugo (Rust kernel + Go user space)  
Status: active aggregate gate

## Goal

Turn the historical X3 package, update, storage-platform, and catalog breadth
backlog into one shared runtime-backed qualification bundle with:

- a real package service on the default Go lane,
- signed metadata verification and trust rotation on replay boot,
- live storage and platform feature exercise on persistent runtime media,
- non-trivial catalog, promotion, telemetry, and rollback-safe distribution flow.

## Report identity

Qualification report schema: `rugo.x3_platform_ecosystem_runtime_report.v1`.
Qualification policy ID: `rugo.x3_platform_ecosystem_runtime_qualification.v1`.

## Historical backlog coverage

The X3 runtime-backed closure covers:

- `M26`
- `M38`
- `M39`

Each backlog must appear in `backlog_closure` with `Runtime-backed` status and
its required runtime checks plus supporting reports.

## Required top-level fields

- `schema`
- `track_id`
- `policy_id`
- `created_utc`
- `seed`
- `gate`
- `capture`
- `checks`
- `summary`
- `backlog_closure`
- `source_reports`
- `artifact_refs`
- `injected_failures`
- `failures`
- `total_failures`
- `gate_pass`
- `digest`

## Runtime checks

The aggregate report must expose these runtime checks:

- `pkgsvc_lifecycle`
- `metadata_rotation`
- `catalog_distribution`
- `storage_platform`
- `pkgsvc_isolation`

`pkgsvc_lifecycle` and `pkgsvc_isolation` bind the default lane to the live
package service rather than only package-policy tooling.

`metadata_rotation` must confirm signed metadata validation on cold boot plus
key rotation and apply markers on replay boot.

`catalog_distribution` must confirm catalog load, staged promotion, install
telemetry, and rollback-safe promotion behavior.

`storage_platform` must confirm snapshot, resize, xattr, reflink, and
capability-negotiation markers on the booted runtime.

## Runtime capture requirements

The capture must include both:

- a `cold_boot` profile
- a `replay_boot` profile

The aggregate report must bind those boots to the shared `pkgsvc`,
update/catalog, and storage/platform markers carried in
`out/booted-runtime-v1.json`.

## Supporting source reports

The aggregate report must bind the historical X3 lane to these supporting
artifacts:

- `out/repo-policy-v3.json`
- `out/pkg-rebuild-v3.json`
- `out/update-trust-v1.json`
- `out/storage-feature-v1.json`
- `out/platform-feature-v1.json`
- `out/app-catalog-sim-v1.json`
- `out/pkg-install-success-v1.json`
- `out/catalog-audit-v1.json`

## Gate binding

- Local gate: `make test-x3-platform-runtime-v1`.
- CI gate: `X3 platform runtime v1 gate`.
- CI artifact: `x3-platform-runtime-v1-artifacts`.
- Primary runtime capture: `out/booted-runtime-v1.json`.
- Primary report: `out/x3-platform-runtime-v1.json`.
