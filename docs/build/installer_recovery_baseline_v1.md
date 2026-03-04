# Installer and Recovery Baseline v1

Date: 2026-03-04  
Milestone: M14 Productization + Release Engineering v1  
Status: active release gate

## Purpose

Define the operator baseline for install, recovery, and support diagnostics.

## Installer baseline

- Installation source: signed release artifact set.
- Required validation before install:
  - checksum verification,
  - update metadata signature verification.
- Install output baseline:
  - bootable image artifact,
  - release metadata retained for audit.

## Recovery baseline

- Recovery mode must support:
  - metadata verification checks,
  - rollback to last trusted sequence,
  - support-bundle generation.
- Recovery operations must be deterministic and scriptable.

## Support bundle baseline

- Tool: `tools/collect_support_bundle_v1.py`
- Output: `out/support-bundle-v1.json`
- Required fields:
  - build and platform metadata,
  - selected artifact checksums,
  - release/update evidence pointers.

## Required release gates

- Local: `make test-release-engineering-v1`
- CI: `Release engineering v1 gate`
