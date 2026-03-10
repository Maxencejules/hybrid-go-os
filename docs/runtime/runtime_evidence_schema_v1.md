# Runtime Evidence Schema v1

Date: 2026-03-10  
Milestone: M40 Runtime-Backed Evidence Integrity v1  
Status: active release gate

## Purpose

Define the machine-readable schema contract for runtime-collected evidence used
by M40 release gates.

## Schema identifiers

- Schema ID: `rugo.runtime_evidence_schema.v1`.
- Primary report schema: `rugo.runtime_evidence_report.v1`.
- Parent evidence policy ID: `rugo.evidence_integrity_policy.v1`.
- Gate provenance policy ID: `rugo.gate_provenance_policy.v1`.

## Required top-level fields

- Top-level field: `schema`.
- Top-level field: `created_utc`.
- Top-level field: `seed`.
- Top-level field: `traces`.
- Top-level field: `evidence_items`.
- Top-level field: `checks`.
- Top-level field: `summary`.
- Top-level field: `digest`.

## Required trace object fields

- Trace field: `trace_id`.
- Trace field: `execution_lane`.
- Trace field: `capture_kind`.
- Trace field: `trace_path`.
- Trace field: `trace_digest`.

## Required evidence item fields

- Evidence field: `artifact_id`.
- Evidence field: `execution_lane`.
- Evidence field: `runtime_source`.
- Evidence field: `synthetic`.
- Evidence field: `trace_id`.
- Evidence field: `trace_digest`.
- Evidence field: `provenance`.
- Evidence field: `signature.valid`.

## Trace linkage rules

- Every evidence item must link to exactly one trace by `trace_id`.
- Evidence and trace lane values must match.
- `trace_digest` in each evidence item must match the linked trace digest.
- Detached evidence items are release-blocking.

## Determinism rules

- Identical seed and inject-failure inputs must produce identical evidence
  payloads, excluding `created_utc`.
- Check ordering is stable and deterministic.
- Deterministic digest algorithm: `sha256`.

## Required artifacts

- `out/runtime-evidence-v1.json`
- `out/gate-evidence-audit-v1.json`
- `out/pytest-evidence-integrity-v1.xml`
- `out/pytest-synthetic-evidence-ban-v1.xml`
