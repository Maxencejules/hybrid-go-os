# Release Attestation Policy v1

Date: 2026-03-09  
Milestone: M31 Release Engineering + Support Lifecycle v2  
Status: active sub-gate

## Objective

Validate attestation continuity across release candidates and block promotions
when policy identity or drift constraints are violated.

## Policy identifiers

- Attestation policy ID: `release-attestation-v1`
- Verification schema: `rugo.release_attestation_verification.v1`

## Verification contract

- `expected_policy_id` must match `observed_policy_id`.
- `policy_match` must be `true`.
- `drift_count` must be less than or equal to `max_drift`.
- Default threshold is `max_drift = 0`.

## Required command

- `python tools/verify_release_attestations_v1.py --release-contract out/release-contract-v1.json --out out/release-attestation-verification-v1.json`

## Enforcement

- Any policy mismatch is gate-blocking.
- Any drift above threshold is gate-blocking.
- Exceptions require explicit policy exception records linked to release notes.
