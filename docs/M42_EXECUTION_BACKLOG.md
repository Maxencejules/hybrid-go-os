# M42 Execution Backlog (Isolation + Namespace Baseline v1)

Date: 2026-03-09  
Lane: Rugo (Rust kernel + Go user space)  
Status: done

## Goal

Add a bounded, testable isolation and resource-control baseline for multi-tenant
service/container workloads.

M42 source of truth remains `docs/M40_M44_GENERAL_PURPOSE_PARITY_ROADMAP.md`,
`MILESTONES.md`, and this backlog.

## Current State Summary

- Compatibility and security hardening lanes are mature but namespace/cgroup
  baseline behavior remains deferred.
- Existing rights/filtering controls provide a foundation but do not yet define
  full isolation/resource-control contract surfaces.
- M42 introduces deterministic containment semantics and release-bound negative
  path enforcement.

## Execution Result

- PR-1: complete (2026-03-10)
- PR-2: complete (2026-03-10)
- PR-3: complete (2026-03-10)

## PR-1: Isolation Contract Freeze

### Objective

Define namespace/cgroup and isolation baseline semantics as executable
contracts.

### Scope

- Add docs:
  - `docs/abi/namespace_cgroup_contract_v1.md`
  - `docs/security/isolation_profile_v1.md`
  - `docs/runtime/resource_control_policy_v1.md`
- Add tests:
  - `tests/security/test_isolation_docs_v1.py`

### Primary files

- `docs/abi/namespace_cgroup_contract_v1.md`
- `docs/security/isolation_profile_v1.md`
- `docs/runtime/resource_control_policy_v1.md`
- `tests/security/test_isolation_docs_v1.py`

### Acceptance checks

- `python -m pytest tests/security/test_isolation_docs_v1.py -v`

### Done criteria for PR-1

- Isolation and resource-control boundaries are explicit, versioned, and
  test-backed.
- Containment policy and failure semantics are machine-verifiable.

### PR-1 completion summary

- Added isolation and resource-control contract docs:
  - `docs/abi/namespace_cgroup_contract_v1.md`
  - `docs/security/isolation_profile_v1.md`
  - `docs/runtime/resource_control_policy_v1.md`
- Added executable contract checks:
  - `tests/security/test_isolation_docs_v1.py`

## PR-2: Isolation Campaign Tooling + Tests

### Objective

Implement deterministic containment and resource-control campaigns, including
escape and misuse negative paths.

### Scope

- Add tooling:
  - `tools/run_isolation_campaign_v1.py`
  - `tools/run_resource_control_campaign_v1.py`
- Add tests:
  - `tests/security/test_namespace_baseline_v1.py`
  - `tests/security/test_cgroup_baseline_v1.py`
  - `tests/security/test_isolation_escape_negative_v1.py`
  - `tests/runtime/test_resource_control_policy_v1.py`

### Primary files

- `tools/run_isolation_campaign_v1.py`
- `tools/run_resource_control_campaign_v1.py`
- `tests/security/test_namespace_baseline_v1.py`
- `tests/security/test_cgroup_baseline_v1.py`
- `tests/security/test_isolation_escape_negative_v1.py`
- `tests/runtime/test_resource_control_policy_v1.py`

### Acceptance checks

- `python tools/run_isolation_campaign_v1.py --out out/isolation-campaign-v1.json`
- `python tools/run_resource_control_campaign_v1.py --out out/resource-control-v1.json`
- `python -m pytest tests/security/test_namespace_baseline_v1.py tests/security/test_cgroup_baseline_v1.py tests/security/test_isolation_escape_negative_v1.py tests/runtime/test_resource_control_policy_v1.py -v`

### Done criteria for PR-2

- Isolation/resource-control artifacts are deterministic and machine-readable.
- Escape and privilege-escalation negative paths are executable and auditable.

### PR-2 completion summary

- Added deterministic isolation/resource-control campaign tooling:
  - `tools/run_isolation_campaign_v1.py`
  - `tools/run_resource_control_campaign_v1.py`
- Added executable baseline and negative-path checks:
  - `tests/security/test_namespace_baseline_v1.py`
  - `tests/security/test_cgroup_baseline_v1.py`
  - `tests/security/test_isolation_escape_negative_v1.py`
  - `tests/runtime/test_resource_control_policy_v1.py`

## PR-3: Isolation Gate + Namespace/Cgroup Sub-gate

### Objective

Make isolation baseline and namespace/cgroup policy checks release-blocking.

### Scope

- Add local gates:
  - `Makefile` target `test-isolation-baseline-v1`
  - `Makefile` target `test-namespace-cgroup-v1`
- Add CI steps:
  - `Isolation baseline v1 gate`
  - `Namespace cgroup v1 gate`
- Add aggregate tests:
  - `tests/security/test_isolation_gate_v1.py`
  - `tests/security/test_namespace_cgroup_gate_v1.py`

### Primary files

- `Makefile`
- `.github/workflows/ci.yml`
- `tests/security/test_isolation_gate_v1.py`
- `tests/security/test_namespace_cgroup_gate_v1.py`
- `MILESTONES.md`
- `docs/STATUS.md`
- `README.md`

### Acceptance checks

- `make test-isolation-baseline-v1`
- `make test-namespace-cgroup-v1`

### Done criteria for PR-3

- Isolation and namespace/cgroup sub-gates are required in local and CI release
  lanes.
- M42 can be marked done only with deterministic isolation artifacts.

### PR-3 completion summary

- Added aggregate gate checks:
  - `tests/security/test_isolation_gate_v1.py`
  - `tests/security/test_namespace_cgroup_gate_v1.py`
- Added local gates:
  - `make test-isolation-baseline-v1`
  - `make test-namespace-cgroup-v1`
- Added CI gates and artifacts:
  - `Isolation baseline v1 gate`
  - `Namespace cgroup v1 gate`
- Updated closure docs:
  - `MILESTONES.md`
  - `docs/STATUS.md`
  - `README.md`

## Non-goals for M42 backlog

- Broad container-orchestration parity claims beyond declared contracts.
- Silent fallback behavior for unsupported containment operations.
