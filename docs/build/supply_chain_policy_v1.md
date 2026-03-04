# Supply Chain Policy v1

Date: 2026-03-04  
Milestone: M14 Productization + Release Engineering v1  
Status: active release gate

## Purpose

Define minimum supply-chain evidence requirements for every release candidate.

## Required artifacts

- SBOM: `out/sbom-v1.spdx.json`
- Provenance: `out/provenance-v1.json`
- Release contract: `out/release-contract-v1.json`
- Update attack report: `out/update-attack-suite-v1.json`

## Evidence generation tools

- `tools/generate_sbom_v1.py`
- `tools/generate_provenance_v1.py`
- `tools/release_contract_v1.py`
- `tools/run_update_attack_suite_v1.py`

## Verification requirements

- Artifact schemas must be versioned and machine-readable.
- SBOM and provenance must be generated in CI for release lanes.
- Reproducibility evidence (`make repro-check`) remains release-blocking.

## Required release gates

- Local: `make test-release-engineering-v1`
- CI: `Release engineering v1 gate`
