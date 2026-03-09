# Rollback Policy v2

Date: 2026-03-09  
Milestone: M20 Operability + Release UX v2  
Status: active release gate

## Purpose

Define deterministic rollback eligibility and mandatory recovery behavior for
release operations.

## Policy

- Rollback is allowed only to the latest trusted sequence that satisfies
  rollback floor constraints.
- Rollback must be triggered automatically on failed post-upgrade health checks.
- Recovery flow must emit a machine-readable drill/report artifact.
- Every rollback incident requires a support bundle before incident closure.

## Drill and evidence requirements

- Tool: `tools/run_upgrade_recovery_drill_v2.py`
- Output: `out/upgrade-recovery-v2.json`
- Required schema: `rugo.upgrade_recovery_drill.v2`
- Required stage names:
  - `upgrade_apply`
  - `post_upgrade_health_check`
  - `rollback_activate`
  - `recovery_bootstrap`

## Required gate

- Local and CI: `test-release-ops-v2`
