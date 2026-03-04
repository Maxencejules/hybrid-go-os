# Release Policy v1

Date: 2026-03-04  
Milestone: M14 Productization + Release Engineering v1  
Status: active release gate

## Purpose

Define a deterministic release governance contract for Rugo so channels,
support windows, and backport rules are executable and auditable.

## Release channels

- `nightly`
  - cadence: daily snapshot
  - support window: 7 days
  - change policy: may include experimental features; no compatibility promises
- `beta`
  - cadence: weekly cut from the release branch
  - support window: until next beta or stable release
  - change policy: feature freeze except release blockers
- `stable`
  - cadence: manual promoted release candidate
  - support window: 90 days baseline
  - change policy: no breaking ABI/profile changes in a stable line

## LTS and backport policy

- LTS candidate: every second stable release.
- LTS support window: 12 months.
- Backport eligibility:
  - security fixes,
  - crash/data-loss regressions,
  - release-blocking correctness defects.
- Non-eligible for backport by default:
  - new feature work,
  - refactors without defect fix,
  - behavior changes that widen unsupported contract scope.

## Ownership and approvals

- Release owner approves channel promotion.
- Update-pipeline owner approves signed update metadata publication.
- Security owner approves key-rotation and signing-policy changes.
- Doc owner approves checklist and release-note changes.

No release is valid unless required owner approvals are recorded.

## Required release artifacts

- `out/release-contract-v1.json`
- `out/update-attack-suite-v1.json`
- `out/sbom-v1.spdx.json`
- `out/provenance-v1.json`

## Required release gates

- Local gate: `make test-release-engineering-v1`
- CI gate: `Release engineering v1 gate`
