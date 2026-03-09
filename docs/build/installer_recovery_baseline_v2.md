# Installer and Recovery Baseline v2

Date: 2026-03-09  
Milestone: M20 Operability + Release UX v2  
Status: active release gate

## Purpose

Define deterministic installer and recovery expectations that are executable in
local and CI release lanes.

## Installer baseline

- Installer contract artifact:
  - `tools/build_installer_v2.py`
  - `out/installer-v2.json`
  - schema: `rugo.installer_contract.v2`
- Preflight checks before install:
  - artifact `sha256` verification,
  - minimum free-space check,
  - update metadata presence check.
- Install outputs:
  - bootable system image,
  - persisted install manifest,
  - release evidence pointers for audit.

## Recovery baseline

- Recovery path must support:
  - rollback to the last trusted sequence,
  - deterministic recovery bootstrapping,
  - support bundle collection for incident triage.
- Recovery drill artifact:
  - `tools/run_upgrade_recovery_drill_v2.py`
  - `out/upgrade-recovery-v2.json`
  - schema: `rugo.upgrade_recovery_drill.v2`

## Required release gates

- Local: `make test-release-ops-v2`
- CI: `Operability and release UX v2 gate`
