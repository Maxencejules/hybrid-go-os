# M14 Execution Backlog (Productization + Release Engineering v1)

Date: 2026-03-04  
Lane: Rugo (Rust kernel + Go user space)

## Goal

Drive M14 from milestone-complete engineering baselines to a shippable product
baseline:

- freeze release/channel/versioning governance as executable contracts,
- implement signed OTA/update workflow with rollback/replay/freeze defenses,
- emit SBOM + provenance artifacts for each release candidate,
- enforce release reproducibility and artifact policy as local/CI gates,
- define installer/recovery/support-bundle operational baseline.

M14 source of truth remains `MILESTONES.md`, `docs/build/*`, `docs/pkg/*`,
`docs/security/*`, and this backlog.

## Current State Summary

- M8-M13 are complete with release-blocking gates for compatibility, hardware,
  security, runtime/toolchain, network, and storage.
- Reproducible image baseline exists (`make repro-check`, `tools/mkimage.sh`,
  `docs/BUILD.md`), but no dedicated release-engineering gate exists yet.
- Security baseline already covers signed boot-manifest + key rotation
  (`tools/secure_boot_manifest_v1.py`, `docs/security/secure_boot_policy_v1.md`).
- Machine-readable report pattern is established (`out/*.json` + CI artifact
  uploads in `.github/workflows/ci.yml`).
- Missing for M14 closure: release policy contract, OTA/update signing and
  client verification flow, SBOM/provenance generation, installer/recovery
  baseline, and release-engineering CI gate.

## Execution Result

- PR-1: complete (2026-03-04)
- PR-2: complete (2026-03-04)
- PR-3: complete (2026-03-04)

## PR-1: Release Contract Freeze + Channel Governance

### Objective

Define release policy/versioning/channel behavior as executable contracts before
update transport implementation.

### Scope

- Add release contract docs:
  - `docs/build/release_policy_v1.md`
  - `docs/build/versioning_scheme_v1.md`
  - `docs/build/release_checklist_v1.md`
- Add contract/report tool:
  - `tools/release_contract_v1.py`
- Add executable checks:
  - `tests/build/test_release_contract_docs_v1.py`
  - `tests/build/test_release_contract_report_v1.py`
- Freeze release-role ownership + escalation flow in release docs.

### Primary files

- `docs/build/release_policy_v1.md`
- `docs/build/versioning_scheme_v1.md`
- `docs/build/release_checklist_v1.md`
- `tools/release_contract_v1.py`
- `tests/build/test_release_contract_docs_v1.py`
- `tests/build/test_release_contract_report_v1.py`

### Acceptance checks

- `python tools/release_contract_v1.py --out out/release-contract-v1.json`
- `python -m pytest tests/build/test_release_contract_docs_v1.py tests/build/test_release_contract_report_v1.py -v`

### Done criteria for PR-1

- Release/channel policy is versioned, reviewable, and test-referenced.
- Backport/support/deprecation rules have no unowned placeholders.
- `out/release-contract-v1.json` schema is stable.

## PR-2: Signed Update Pipeline + Rollback Protection

### Objective

Build deterministic signed OTA/update baseline with explicit anti-replay,
anti-freeze, and rollback-protection behavior.

### Scope

- Add update/repository/signing docs:
  - `docs/pkg/update_protocol_v1.md`
  - `docs/pkg/update_repo_layout_v1.md`
  - `docs/security/update_signing_policy_v1.md`
- Add update tooling:
  - `tools/update_repo_sign_v1.py`
  - `tools/update_client_verify_v1.py`
  - `tools/run_update_attack_suite_v1.py`
- Add executable checks:
  - `tests/pkg/test_update_metadata_v1.py`
  - `tests/pkg/test_update_rollback_protection_v1.py`
  - `tests/pkg/test_update_attack_suite_v1.py`

### Primary files

- `docs/pkg/update_protocol_v1.md`
- `docs/pkg/update_repo_layout_v1.md`
- `docs/security/update_signing_policy_v1.md`
- `tools/update_repo_sign_v1.py`
- `tools/update_client_verify_v1.py`
- `tools/run_update_attack_suite_v1.py`
- `tests/pkg/test_update_metadata_v1.py`
- `tests/pkg/test_update_rollback_protection_v1.py`
- `tests/pkg/test_update_attack_suite_v1.py`

### Acceptance checks

- `python tools/update_repo_sign_v1.py --repo out/update-repo-v1 --out out/update-metadata-v1.json`
- `python tools/update_client_verify_v1.py --repo out/update-repo-v1 --expect-version 1.0.0`
- `python tools/run_update_attack_suite_v1.py --seed 20260304 --out out/update-attack-suite-v1.json`
- `python -m pytest tests/pkg/test_update_metadata_v1.py tests/pkg/test_update_rollback_protection_v1.py tests/pkg/test_update_attack_suite_v1.py -v`

### Done criteria for PR-2

- Update metadata/targets are signed and client-verifiable with documented
  key-rotation behavior.
- Replay/freeze/rollback simulations have deterministic pass/fail outcomes.
- Update artifact schemas are stable and machine-readable.

## PR-3: Supply-Chain + Reproducibility Gate + Milestone Closure

### Objective

Promote release engineering checks to mandatory local/CI gates and close M14
status docs with evidence pointers.

### Scope

- Add supply-chain policy/docs/tools:
  - `docs/build/supply_chain_policy_v1.md`
  - `tools/generate_sbom_v1.py`
  - `tools/generate_provenance_v1.py`
- Add installer/recovery baseline docs/tooling:
  - `docs/build/installer_recovery_baseline_v1.md`
  - `tools/collect_support_bundle_v1.py`
- Add aggregate gate checks:
  - `tests/build/test_release_engineering_gate_v1.py`
- Add local gate:
  - `Makefile` target `test-release-engineering-v1`
- Add CI gate:
  - `.github/workflows/ci.yml` step `Release engineering v1 gate`
- Wire release artifacts:
  - `out/release-contract-v1.json`
  - `out/update-attack-suite-v1.json`
  - `out/sbom-v1.spdx.json`
  - `out/provenance-v1.json`
- Mark M14 done in milestone/status docs once gates are green.

### Primary files

- `docs/build/supply_chain_policy_v1.md`
- `docs/build/installer_recovery_baseline_v1.md`
- `tools/generate_sbom_v1.py`
- `tools/generate_provenance_v1.py`
- `tools/collect_support_bundle_v1.py`
- `tests/build/test_release_engineering_gate_v1.py`
- `Makefile`
- `.github/workflows/ci.yml`
- `MILESTONES.md`
- `docs/STATUS.md`
- `README.md`
- `docs/POST_G2_EXTENDED_MILESTONES.md`

### Acceptance checks

- `make test-release-engineering-v1`
- `make repro-check`
- `python tools/generate_sbom_v1.py --out out/sbom-v1.spdx.json`
- `python tools/generate_provenance_v1.py --out out/provenance-v1.json`
- `python -m pytest tests/build/test_release_engineering_gate_v1.py -v`

### Done criteria for PR-3

- Release-engineering gate is required in local and CI release lanes.
- Reproducibility/update-security/SBOM/provenance artifacts are generated and
  stable for milestone evidence.
- M14 status is marked `done` with clear evidence pointers.

## Non-goals for M14 backlog

- Full enterprise fleet-management control plane.
- Broad hardware-specific installer UX permutations beyond current baseline.
- End-to-end package ecosystem governance beyond update/release policy scope.
