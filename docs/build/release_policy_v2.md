# Release Policy v2

Date: 2026-03-09  
Milestone: M31 Release Engineering + Support Lifecycle v2  
Status: active release gate

## Objective

Define executable release lifecycle governance for branch strategy, support
windows, and mandatory supply-chain revalidation on every release candidate.

## Policy identifiers

- Release lifecycle policy ID: `rugo.release_policy.v2`
- Branch audit schema: `rugo.release_branch_audit.v2`
- Support window audit schema: `rugo.support_window_audit.v1`
- Supply-chain revalidation schema: `rugo.supply_chain_revalidation_report.v1`
- Release attestation verification schema: `rugo.release_attestation_verification.v1`

## Release channels and branch model

- `nightly`
  - source branch: `main`
  - cadence: daily snapshot
  - support window: 14 days
- `beta`
  - source branch: `release/<major>.<minor>`
  - cadence: weekly cut
  - support window: 45 days
- `stable`
  - source branch: `release/<major>.<minor>`
  - cadence: manual promotion
  - support window: 180 days
- `lts`
  - source branch: `release/<major>.<minor>`
  - cadence: selected stable promotions
  - support window: 730 days

Required branch naming policy:

- stable and beta lanes must use `release/<major>.<minor>`
- emergency patches may use `hotfix/<major>.<minor>.<patch>`
- non-conforming branch names are release-blocking

## Support and backport obligations

- Security fixes are mandatory for active `stable` and `lts` branches.
- Security fix SLA must be less than or equal to 14 days.
- Backport window for security and release-blocker fixes must be at least 21 days.
- Any support-window or backport exception requires an explicit policy exception record.

## Required release candidate checks

- Bundle assembly command:
  - `python tools/build_release_bundle_v1.py --out out/release-bundle-v1.json`
- Branch audit command:
  - `python tools/release_branch_audit_v2.py --release-bundle out/release-bundle-v1.json --out out/release-branch-audit-v2.json`
- Support window audit command:
  - `python tools/support_window_audit_v1.py --release-bundle out/release-bundle-v1.json --out out/support-window-audit-v1.json`
- Supply-chain revalidation sub-gate:
  - `make test-supply-chain-revalidation-v1`

Release lifecycle v2 gate is valid only when all checks pass with
`max_failures = 0`.

## Required gates

- Local gate: `make test-release-lifecycle-v2`
- CI gate: `Release lifecycle v2 gate`
- CI sub-gate: `Supply-chain revalidation v1 gate`
