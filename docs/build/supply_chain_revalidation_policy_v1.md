# Supply Chain Revalidation Policy v1

Date: 2026-03-09  
Milestone: M31 Release Engineering + Support Lifecycle v2  
Status: active sub-gate

## Objective

Revalidate SBOM/provenance integrity and attestation drift for every release
candidate before promotion.

## Policy identifiers

- Supply-chain policy ID: `rugo.supply_chain_revalidation_policy.v1`
- Revalidation report schema: `rugo.supply_chain_revalidation_report.v1`
- Attestation verification schema: `rugo.release_attestation_verification.v1`

## Mandatory checks

- `sbom_exists`
- `sbom_schema`
- `provenance_exists`
- `provenance_schema`
- `subject_consistency`

All mandatory checks must pass with `max_failures = 0`.

## Drift and exception rules

- Attestation drift threshold: `max_drift = 0`.
- `policy_match` must be `true`.
- Drift or policy mismatch is gate-blocking.
- Policy exceptions require explicit exception records.

## Required tools and artifacts

- `python tools/build_release_bundle_v1.py --out out/release-bundle-v1.json`
- `python tools/verify_sbom_provenance_v2.py --out out/supply-chain-revalidation-v1.json`
- `python tools/verify_release_attestations_v1.py --out out/release-attestation-verification-v1.json`
- `out/release-bundle-v1.json`
- `out/sbom-v1.spdx.json`
- `out/provenance-v1.json`

## Required gates

- Local gate: `make test-supply-chain-revalidation-v1`
- CI gate: `Supply-chain revalidation v1 gate`
- Lifecycle integration: `make test-release-lifecycle-v2`
