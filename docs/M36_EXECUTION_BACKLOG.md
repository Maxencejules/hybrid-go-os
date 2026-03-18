# M36 Execution Backlog (Compatibility Surface Expansion v1)

Date: 2026-03-09  
Lane: Rugo (Rust kernel + Go user space)  
Status: done

## Goal

Expand high-impact compatibility surfaces beyond current subset boundaries
while preserving deterministic unsupported behavior for deferred features.

M36 source of truth remains `docs/M35_M39_GENERAL_PURPOSE_EXPANSION_ROADMAP.md`,
`MILESTONES.md`, and this backlog.

## Current State Summary

- Compatibility profile and syscall matrices still explicitly defer key surfaces
  (`fork`/`clone`, `epoll`/`io_uring`, namespace/cgroup, socket-family parity).
- App compatibility gates are stable for bounded classes and thresholds.
- M36 introduces compatibility profile v4 planning and deterministic closure of
  prioritized gaps.

## Execution Result

- PR-1: complete (2026-03-09)
- PR-2: complete (2026-03-09)
- PR-3: complete (2026-03-09)

## PR-1: Compatibility Contract Freeze

### Objective

Define compatibility profile v4 and explicit closure/defer policy for expanded
surfaces.

### Scope

- Add docs:
  - `docs/abi/compat_profile_v4.md`
  - `docs/runtime/syscall_coverage_matrix_v3.md`
  - `docs/abi/process_model_v3.md`
  - `docs/abi/socket_family_expansion_v1.md`
- Add tests:
  - `tests/compat/test_compat_docs_v4.py`

### Primary files

- `docs/abi/compat_profile_v4.md`
- `docs/runtime/syscall_coverage_matrix_v3.md`
- `docs/abi/process_model_v3.md`
- `docs/abi/socket_family_expansion_v1.md`
- `tests/compat/test_compat_docs_v4.py`

### Acceptance checks

- `python -m pytest tests/compat/test_compat_docs_v4.py -v`

### Done criteria for PR-1

- Compatibility profile v4 boundaries are explicit, versioned, and test-backed.

### PR-1 completion summary

- Added compatibility contract docs:
  - `docs/abi/compat_profile_v4.md`
  - `docs/runtime/syscall_coverage_matrix_v3.md`
  - `docs/abi/process_model_v3.md`
  - `docs/abi/socket_family_expansion_v1.md`
- Added executable contract checks:
  - `tests/compat/test_compat_docs_v4.py`

## PR-2: Compatibility Closure Campaign

### Objective

Implement deterministic compatibility expansion and deferred-surface behavior
checks.

### Scope

- Add tooling:
  - `tools/run_compat_surface_campaign_v1.py`
  - `tools/run_posix_gap_report_v1.py`
- Add tests:
  - `tests/compat/test_posix_gap_closure_v1.py`
  - `tests/compat/test_process_model_v3.py`
  - `tests/compat/test_socket_family_expansion_v1.py`
  - `tests/compat/test_deferred_surface_behavior_v1.py`

### Primary files

- `tools/run_compat_surface_campaign_v1.py`
- `tools/run_posix_gap_report_v1.py`
- `tests/compat/test_posix_gap_closure_v1.py`
- `tests/compat/test_process_model_v3.py`
- `tests/compat/test_socket_family_expansion_v1.py`
- `tests/compat/test_deferred_surface_behavior_v1.py`

### Acceptance checks

- `python tools/run_compat_surface_campaign_v1.py --out out/compat-surface-v1.json`
- `python tools/run_posix_gap_report_v1.py --out out/posix-gap-report-v1.json`
- `python -m pytest tests/compat/test_posix_gap_closure_v1.py tests/compat/test_process_model_v3.py tests/compat/test_socket_family_expansion_v1.py tests/compat/test_deferred_surface_behavior_v1.py -v`

### Done criteria for PR-2

- Expanded compatibility behavior is deterministic and machine-verifiable.
- Deferred surfaces remain explicit with deterministic unsupported outcomes.

### PR-2 completion summary

- Added deterministic compatibility campaign tooling:
  - `tools/run_compat_surface_campaign_v1.py`
  - `tools/run_posix_gap_report_v1.py`
- Added executable compatibility checks:
  - `tests/compat/test_posix_gap_closure_v1.py`
  - `tests/compat/test_process_model_v3.py`
  - `tests/compat/test_socket_family_expansion_v1.py`
  - `tests/compat/test_deferred_surface_behavior_v1.py`

## PR-3: Compatibility Surface Gate + POSIX Sub-gate

### Objective

Make compatibility expansion release-blocking.

### Scope

- Add local gates:
  - `Makefile` target `test-compat-surface-v1`
  - `Makefile` target `test-posix-gap-closure-v1`
- Add CI steps:
  - `Compatibility surface v1 gate`
  - `POSIX gap closure v1 gate`
- Add aggregate tests:
  - `tests/compat/test_compat_surface_gate_v1.py`
  - `tests/compat/test_posix_gap_closure_gate_v1.py`

### Primary files

- `Makefile`
- `.github/workflows/ci.yml`
- `tests/compat/test_compat_surface_gate_v1.py`
- `tests/compat/test_posix_gap_closure_gate_v1.py`
- `MILESTONES.md`
- `docs/STATUS.md`
- `README.md`

### Acceptance checks

- `make test-compat-surface-v1`
- `make test-posix-gap-closure-v1`

### Done criteria for PR-3

- Compatibility surface and POSIX closure sub-gates are required in local and CI.
- M36 can be marked done with deterministic campaign artifacts.

### PR-3 completion summary

- Added aggregate gate checks:
  - `tests/compat/test_compat_surface_gate_v1.py`
  - `tests/compat/test_posix_gap_closure_gate_v1.py`
- Added local gates:
  - `make test-compat-surface-v1`
  - `make test-posix-gap-closure-v1`
- Added CI gates and artifacts:
  - `Compatibility surface v1 gate`
  - `POSIX gap closure v1 gate`
- Updated closure docs:
  - `MILESTONES.md`
  - `docs/STATUS.md`
  - `README.md`

## X1 runtime-backed closure addendum (2026-03-18)

- Added a runtime-backed compatibility corpus that exercises loader, file,
  readiness, process, and socket paths with real ELF apps on the default lane.
- `make test-compat-surface-v1` now depends on `make test-real-compat-runtime-v1`
  so the expanded surface is proven in the live runtime, not only in campaign
  reports.
- Deferred boundary behavior is now probed in the runtime corpus itself for the
  explicit unsupported `fork`, `clone`, and `epoll` syscall slots.

## Non-goals for M36 backlog

- Unbounded "full Linux parity" claims in a single release cycle.
- Implicitly supporting deferred APIs without explicit contract updates.
