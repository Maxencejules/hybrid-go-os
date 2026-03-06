# Supply Chain Revalidation Policy v1

Status: draft  
Version: v1

## Objective

Revalidate SBOM, provenance, and release signatures for every release candidate.

## Policy

- SBOM schema and package identity must match release metadata.
- Provenance subjects must align with shipped artifacts.
- Any attestation drift is gate-blocking unless explicitly waived.

## Evidence

- Artifact schema: `rugo.supply_chain_revalidation_report.v1`.
- Gate: `test-supply-chain-revalidation-v1`.

