# Storage Recovery Playbook v1

Date: 2026-03-04  
Milestone: M13 Storage Reliability v1

## Goal

Provide a deterministic operator workflow for storage integrity checks and
recovery actions in CI and local environments.

## Check workflow

1. Run recovery checker:
   - `python tools/storage_recover_v1.py --check --out out/storage-recovery-v1.json`
2. Confirm required fields:
   - `schema == rugo.storage_recovery_report.v1`
   - `mountable == true`
   - `total_issues == 0`
3. If check fails, inspect failed check rows and sequence markers.

## Fault-campaign workflow

1. Run campaign tool:
   - `python tools/run_storage_fault_campaign_v1.py --seed 20260304 --out out/storage-fault-campaign-v1.json`
2. Confirm thresholds:
   - `schema == rugo.storage_fault_campaign_report.v1`
   - `total_failures <= max_failures`
3. Preserve report artifacts for CI upload and incident triage.

## Escalation policy

- Any recovery check regression is release-blocking for M13.
- Any fault-campaign threshold breach is release-blocking for M13.
- Recovery regressions require root-cause notes and updated negative-path tests.
