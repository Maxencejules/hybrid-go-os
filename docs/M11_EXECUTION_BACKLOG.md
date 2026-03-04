# M11 Execution Backlog (Runtime + Toolchain Maturity v1)

Date: 2026-03-04  
Lane: Rugo (Rust kernel + Go user space)

## Goal

Drive M11 to an executable runtime/toolchain maturity baseline:

- freeze a `GOOS=rugo` runtime-port contract,
- publish runtime syscall coverage with owned gap policy,
- provide reproducible bootstrap and contract artifacts,
- add a release-blocking runtime qualification gate in local/CI lanes,
- publish maintainership and deprecation workflow.

M11 source of truth remains `MILESTONES.md`, `docs/runtime/*`, and this backlog.

## Current State Summary

- M10 security baseline v1 is complete and release-gated.
- G2 already proved stock-Go artifact generation and execution markers.
- Toolchain and runtime work existed but lacked:
  - a consolidated runtime contract,
  - explicit coverage ownership for runtime-facing syscall behavior,
  - a dedicated runtime maturity gate.

## Execution Result

- PR-1: complete (2026-03-04)
- PR-2: complete (2026-03-04)
- PR-3: complete (2026-03-04)

## PR-1: Runtime Contract + Coverage Matrix

### Objective

Define the runtime-port compatibility contract and make syscall coverage
auditable.

### Scope

- Add runtime contract docs:
  - `docs/runtime/port_contract_v1.md`
  - `docs/runtime/syscall_coverage_matrix_v1.md`
  - `docs/runtime/abi_stability_policy_v1.md`
- Add contract doc checks:
  - `tests/runtime/test_runtime_contract_docs_v1.py`
  - `tests/runtime/test_runtime_abi_window_v1.py`

### Done criteria

- Runtime-facing syscall coverage has explicit status + owner rows.
- ABI stability window and deprecation workflow are documented.

## PR-2: Bootstrap + Reproducibility Tooling

### Objective

Provide deterministic setup/check tooling for the runtime/toolchain lane.

### Scope

- Add bootstrap checker:
  - `tools/bootstrap_go_port_v1.sh`
- Add runtime contract/repro artifact tool:
  - `tools/runtime_toolchain_contract_v1.py`
- Add bootstrap/repro docs:
  - `docs/runtime/toolchain_bootstrap_v1.md`

### Done criteria

- Bootstrap check validates required tools/files for the runtime lane.
- Contract and repro artifacts are emitted under `out/`.

## PR-3: Runtime Gate + Milestone Closure

### Objective

Wire M11 into required local and CI gates and close status docs.

### Scope

- Add runtime qualification tests:
  - `tests/runtime/test_runtime_stress_v1.py`
- Add local gate:
  - `Makefile` target `test-runtime-maturity`
- Add CI gate:
  - `.github/workflows/ci.yml` step `Runtime + toolchain maturity v1 gate`
- Add maintainers/process doc:
  - `docs/runtime/maintainers_v1.md`
- Mark M11 done in milestone/status/readme docs.

### Done criteria

- Runtime maturity gate is executable locally and in CI.
- Milestone docs include evidence pointers to runtime/toolchain artifacts.

## Acceptance checks

- `bash tools/bootstrap_go_port_v1.sh --check`
- `python tools/runtime_toolchain_contract_v1.py --out out/runtime-toolchain-contract.env`
- `python tools/runtime_toolchain_contract_v1.py --repro --out out/runtime-toolchain-repro.json`
- `make test-runtime-maturity`

## Non-goals for M11 backlog

- Full upstream-Go port acceptance beyond the current Rugo contract lane.
- Complete network/storage parity work (owned by M12/M13).
- Broad non-QEMU host runtime qualification.
