# Update Protocol v1

Date: 2026-03-04  
Milestone: M14 Productization + Release Engineering v1  
Status: active release gate

## Purpose

Define a deterministic signed update metadata protocol for release channels.

## Metadata schema

- Schema ID: `rugo.update_metadata.v1`
- Required fields:
  - `channel`
  - `version`
  - `build_sequence`
  - `created_utc`
  - `expires_utc`
  - `targets[]` (`path`, `sha256`, `size`)
  - `signature` (`key_id`, `alg`, `value`)

## Client verification rules

- Reject metadata with invalid signature.
- Reject metadata whose `build_sequence` is not strictly greater than the last
  trusted sequence for that channel.
- Reject metadata whose `expires_utc` is in the past.
- Reject metadata whose target digest/size does not match repository content.

## Required tools and tests

- Tools:
  - `tools/update_repo_sign_v1.py`
  - `tools/update_client_verify_v1.py`
  - `tools/run_update_attack_suite_v1.py`
- Tests:
  - `tests/pkg/test_update_metadata_v1.py`
  - `tests/pkg/test_update_rollback_protection_v1.py`
  - `tests/pkg/test_update_attack_suite_v1.py`
