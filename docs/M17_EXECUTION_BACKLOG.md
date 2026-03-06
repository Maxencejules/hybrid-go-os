# M17 Execution Backlog (Compatibility Profile v2)

Date: 2026-03-06  
Lane: Rugo (Rust kernel + Go user space)  
Status: done

## Goal

Increase external software viability via ABI/loader contract maturity, POSIX
subset expansion, and deterministic compatibility tier gating.

M17 source of truth remains `docs/M15_M20_MULTIPURPOSE_PLAN.md`,
`MILESTONES.md`, and this backlog.

## Current State Summary

- Compatibility profile v1 and package external-app lane are already complete.
- ABI + loader v1 contracts are stable and test-backed.
- M17 closes v2 profile scope, deterministic tier thresholds, and release gates.

## Execution Result

- PR-1: complete (2026-03-06)
- PR-2: complete (2026-03-06)
- PR-3: complete (2026-03-06)

## PR-1: ABI + Loader Contract v2

### Objective

Freeze ABI and loader v2 expectations before expanding POSIX/profile coverage.

### Scope

- Add docs:
  - `docs/abi/syscall_v2.md`
  - `docs/abi/compat_profile_v2.md`
  - `docs/abi/elf_loader_contract_v2.md`
- Add tests:
  - `tests/compat/test_abi_profile_v2_docs.py`
  - `tests/compat/test_elf_loader_dynamic_v2.py`

### Primary files

- `docs/abi/syscall_v2.md`
- `docs/abi/compat_profile_v2.md`
- `docs/abi/elf_loader_contract_v2.md`
- `tests/compat/test_abi_profile_v2_docs.py`
- `tests/compat/test_elf_loader_dynamic_v2.py`

### Acceptance checks

- `python -m pytest tests/compat/test_abi_profile_v2_docs.py tests/compat/test_elf_loader_dynamic_v2.py -v`

### Done criteria for PR-1

- ABI/profile docs are versioned and executable-check referenced.
- Loader contract behavior is deterministic for covered profiles.

### PR-1 completion summary

- Added v2 ABI/profile/loader contracts with explicit IDs, freeze/deprecation
  policy, dynamic loader constraints, and deterministic failure classes.
- Added executable checks for:
  - v2 doc contract tokens + kernel dispatch wiring,
  - deterministic static/dynamic loader model behavior.

## PR-2: POSIX Subset Expansion + External App Tier

### Objective

Define v2 syscall coverage and external app tier pass thresholds.

### Scope

- Add docs:
  - `docs/runtime/syscall_coverage_matrix_v2.md`
- Add tests:
  - `tests/compat/test_posix_profile_v2.py`
  - `tests/compat/test_external_apps_tier_v2.py`
- Add fixture model:
  - `tests/compat/v2_model.py`

### Primary files

- `docs/runtime/syscall_coverage_matrix_v2.md`
- `tests/compat/test_posix_profile_v2.py`
- `tests/compat/test_external_apps_tier_v2.py`
- `tests/compat/v2_model.py`

### Acceptance checks

- `python -m pytest tests/compat/test_posix_profile_v2.py tests/compat/test_external_apps_tier_v2.py -v`

### Done criteria for PR-2

- Supported/unsupported profile surfaces are explicit.
- External app tier thresholds are deterministic and repeatable.

### PR-2 completion summary

- Added runtime syscall coverage matrix v2 with owner/target evidence rows.
- Added deterministic v2 model for:
  - dynamic loader acceptance/rejection,
  - POSIX surface required/optional/unsupported classification,
  - external app tier threshold evaluation and digest output.
- Added signed metadata + threshold tests for tiered external app behavior and
  QEMU runtime marker checks for Tier B (`GOSTD: ok`).

## PR-3: Compatibility Gate + CI Promotion

### Objective

Make compatibility profile v2 a release-blocking gate.

### Scope

- Add aggregate test:
  - `tests/compat/test_compat_gate_v2.py`
- Add local gate:
  - `Makefile` target `test-compat-v2`
- Add CI gate:
  - `.github/workflows/ci.yml` step `Compatibility profile v2 gate`

### Primary files

- `tests/compat/test_compat_gate_v2.py`
- `Makefile`
- `.github/workflows/ci.yml`
- `MILESTONES.md`
- `docs/STATUS.md`

### Acceptance checks

- `make test-compat-v2`

### Done criteria for PR-3

- Compatibility profile v2 gate is required in local and CI release lanes.
- M17 status can be marked done with evidence pointers.

### PR-3 completion summary

- Added aggregate gate test for M17 artifact + wiring closure.
- Added local gate:
  - `make test-compat-v2`
  - JUnit output: `out/pytest-compat-v2.xml`
- Added CI gate step + artifact upload:
  - step: `Compatibility profile v2 gate`
  - artifact: `compat-v2-junit`
- Updated milestone/status documents to mark M17 done with evidence links.

## Non-goals for M17 backlog

- Full Linux distribution compatibility parity.
- Broad GUI/desktop runtime compatibility scope.
