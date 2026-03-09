# Operations Runbook v2

Date: 2026-03-09  
Milestone: M20 Operability + Release UX v2  
Status: active release gate

## Purpose

Document the operator flow for install, upgrade, rollback, recovery, and
support bundle capture.

## Standard flow

1. Build installer contract:
   - `python tools/build_installer_v2.py --out out/installer-v2.json`
2. Run upgrade and recovery drill:
   - `python tools/run_upgrade_recovery_drill_v2.py --out out/upgrade-recovery-v2.json`
3. Collect support bundle:
   - `python tools/collect_support_bundle_v2.py --artifacts out/installer-v2.json out/upgrade-recovery-v2.json --out out/support-bundle-v2.json`
4. Run gate:
   - `make test-release-ops-v2`

## Rollback and recovery triggers

- Trigger rollback when post-upgrade health checks fail.
- Roll back only to artifacts at or above the documented rollback floor.
- Require a support bundle for every rollback/recovery incident.

## Incident triage checklist

- Capture exact command line and timestamp.
- Preserve `installer-v2`, `upgrade-recovery-v2`, and `support-bundle-v2` artifacts.
- Record whether rollback was automatic or operator-initiated.
- Link incident to release channel and build sequence.
