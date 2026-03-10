# M40 Execution Backlog (Runtime-Backed Evidence Integrity v1)

Date: 2026-03-09  
Lane: Rugo (Rust kernel + Go user space)  
Status: done

## Goal

Convert release-bound evidence from deterministic synthetic-only reports to
runtime-backed artifacts with explicit provenance and auditability.

M40 source of truth remains `docs/M40_M44_GENERAL_PURPOSE_PARITY_ROADMAP.md`,
`MILESTONES.md`, and this backlog.

## Current State Summary

- M35-M39 gates are green but several campaign artifacts are generated from
  seeded model tooling rather than runtime-collected execution evidence.
- Compatibility profile v4 still relies on deterministic deferred-surface
  behavior and requires stronger runtime provenance for release claims.
- Hardware/desktop/ecosystem claims are bounded and need evidence-integrity
  promotion before broader parity claims.

## Execution Result

- PR-1: complete (2026-03-10)
- PR-2: complete (2026-03-10)
- PR-3: complete (2026-03-10)

## PR-1: Evidence Integrity Contract Freeze

### Objective

Define M40 evidence provenance and synthetic-artifact policy as executable
contracts.

### Scope

- Add docs:
  - `docs/runtime/evidence_integrity_policy_v1.md`
  - `docs/runtime/runtime_evidence_schema_v1.md`
  - `docs/runtime/gate_provenance_policy_v1.md`
- Add tests:
  - `tests/runtime/test_evidence_integrity_docs_v1.py`

### Primary files

- `docs/runtime/evidence_integrity_policy_v1.md`
- `docs/runtime/runtime_evidence_schema_v1.md`
- `docs/runtime/gate_provenance_policy_v1.md`
- `tests/runtime/test_evidence_integrity_docs_v1.py`

### Acceptance checks

- `python -m pytest tests/runtime/test_evidence_integrity_docs_v1.py -v`

### Done criteria for PR-1

- Evidence integrity policy is explicit, versioned, and test-backed.
- Runtime provenance requirements are machine-checkable.

### PR-1 completion summary

- Added evidence-integrity contract docs:
  - `docs/runtime/evidence_integrity_policy_v1.md`
  - `docs/runtime/runtime_evidence_schema_v1.md`
  - `docs/runtime/gate_provenance_policy_v1.md`
- Added executable contract checks:
  - `tests/runtime/test_evidence_integrity_docs_v1.py`

## PR-2: Runtime Evidence Collection + Audit Tooling

### Objective

Implement deterministic collection of runtime evidence and enforce provenance
audits over release-bound artifacts.

### Scope

- Add tooling:
  - `tools/collect_runtime_evidence_v1.py`
  - `tools/audit_gate_evidence_v1.py`
- Add tests:
  - `tests/runtime/test_runtime_evidence_collection_v1.py`
  - `tests/runtime/test_gate_evidence_audit_v1.py`
  - `tests/runtime/test_evidence_trace_linkage_v1.py`

### Primary files

- `tools/collect_runtime_evidence_v1.py`
- `tools/audit_gate_evidence_v1.py`
- `tests/runtime/test_runtime_evidence_collection_v1.py`
- `tests/runtime/test_gate_evidence_audit_v1.py`
- `tests/runtime/test_evidence_trace_linkage_v1.py`

### Acceptance checks

- `python tools/collect_runtime_evidence_v1.py --out out/runtime-evidence-v1.json`
- `python tools/audit_gate_evidence_v1.py --out out/gate-evidence-audit-v1.json`
- `python -m pytest tests/runtime/test_runtime_evidence_collection_v1.py tests/runtime/test_gate_evidence_audit_v1.py tests/runtime/test_evidence_trace_linkage_v1.py -v`

### Done criteria for PR-2

- Runtime evidence artifacts are deterministic, machine-readable, and linked to
  execution traces.
- Provenance audit fails deterministically when synthetic-only artifacts are
  provided.

### PR-2 completion summary

- Added deterministic runtime evidence tooling:
  - `tools/collect_runtime_evidence_v1.py`
  - `tools/audit_gate_evidence_v1.py`
- Added executable runtime evidence checks:
  - `tests/runtime/test_runtime_evidence_collection_v1.py`
  - `tests/runtime/test_gate_evidence_audit_v1.py`
  - `tests/runtime/test_evidence_trace_linkage_v1.py`

## PR-3: Evidence Integrity Gate + Synthetic-Evidence Ban Sub-gate

### Objective

Make evidence provenance enforcement release-blocking.

### Scope

- Add local gates:
  - `Makefile` target `test-evidence-integrity-v1`
  - `Makefile` target `test-synthetic-evidence-ban-v1`
- Add CI steps:
  - `Evidence integrity v1 gate`
  - `Synthetic evidence ban v1 gate`
- Add aggregate tests:
  - `tests/runtime/test_evidence_integrity_gate_v1.py`
  - `tests/runtime/test_synthetic_evidence_ban_v1.py`

### Primary files

- `Makefile`
- `.github/workflows/ci.yml`
- `tests/runtime/test_evidence_integrity_gate_v1.py`
- `tests/runtime/test_synthetic_evidence_ban_v1.py`
- `MILESTONES.md`
- `docs/STATUS.md`
- `README.md`

### Acceptance checks

- `make test-evidence-integrity-v1`
- `make test-synthetic-evidence-ban-v1`

### Done criteria for PR-3

- Evidence-integrity and synthetic-ban sub-gates are required in local and CI
  release lanes.
- M40 can be marked done only with runtime-provenance artifacts.

### PR-3 completion summary

- Added aggregate gate checks:
  - `tests/runtime/test_evidence_integrity_gate_v1.py`
  - `tests/runtime/test_synthetic_evidence_ban_v1.py`
- Added local gates:
  - `make test-evidence-integrity-v1`
  - `make test-synthetic-evidence-ban-v1`
- Added CI gates and artifacts:
  - `Evidence integrity v1 gate`
  - `Synthetic evidence ban v1 gate`
- Updated closure docs:
  - `MILESTONES.md`
  - `docs/STATUS.md`
  - `README.md`

## Non-goals for M40 backlog

- Expanding syscall/hardware scope without evidence-provenance closure first.
- Claiming Linux/Windows parity from synthetic campaign outputs.
