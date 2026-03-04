# Release Checklist v1

Date: 2026-03-04  
Milestone: M14 Productization + Release Engineering v1  
Status: active release gate

## Purpose

Provide an operator checklist for release candidate assembly, sign-off, and
post-release validation.

## Pre-release checks

- Confirm branch and target channel (`nightly`, `beta`, or `stable`).
- Run release gate locally:
  - `make test-release-engineering-v1`
  - `make repro-check`
- Confirm artifacts generated:
  - `out/release-contract-v1.json`
  - `out/update-attack-suite-v1.json`
  - `out/sbom-v1.spdx.json`
  - `out/provenance-v1.json`

## Signing and metadata checks

- Sign update repository metadata with current active key.
- Verify update metadata with client verification tool.
- Run rollback/replay/freeze attack suite:
  - `python tools/run_update_attack_suite_v1.py --seed 20260304 --out out/update-attack-suite-v1.json`

## Release publication

- Publish release notes with known limitations.
- Publish artifact checksums and provenance links.
- Attach support-bundle guidance for operators.

## Post-release validation

- Validate update success and rollback metrics.
- Confirm no release-gate regressions in CI reruns.
- Record evidence pointers in `docs/STATUS.md` and `MILESTONES.md`.
