# Update Protocol v2

Date: 2026-03-09  
Milestone: M20 Operability + Release UX v2  
Status: active release gate

## Purpose

Define the deterministic update metadata contract for upgrade, rollback
eligibility, and recovery drill integration.

## Metadata schema

- Schema ID: `rugo.update_metadata.v2`
- Required fields:
  - `channel`
  - `version`
  - `build_sequence`
  - `rollback_floor_sequence`
  - `created_utc`
  - `expires_utc`
  - `recovery_plan_id`
  - `targets[]` (`path`, `sha256`, `size`)
  - `signature` (`key_id`, `alg`, `value`)

## Client verification rules

- Reject metadata with invalid signature.
- Reject metadata whose `build_sequence` is not strictly greater than local
  trusted state.
- Reject metadata whose `build_sequence` is below `rollback_floor_sequence`.
- Reject metadata whose `expires_utc` is in the past.
- Reject metadata whose targets do not match repository digest/size.

## Required tools and tests

- Tools:
  - `tools/run_upgrade_recovery_drill_v2.py`
  - `tools/collect_support_bundle_v2.py`
- Tests:
  - `tests/build/test_upgrade_rollback_v2.py`
  - `tests/build/test_support_bundle_v2.py`
