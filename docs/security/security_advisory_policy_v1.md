# Security Advisory Policy v1

Date: 2026-03-09  
Milestone: M28 Security Hardening Program v3  
Status: active required sub-gate

## Purpose

Define schema and publication requirements for machine-validated security
advisories.

## Contract identifiers

- Policy ID: `rugo.security_advisory_policy.v1`
- Lint report schema: `rugo.security_advisory_lint_report.v1`
- Linked response policy: `rugo.vulnerability_response_policy.v1`

## Advisory schema requirements

Required fields:

- advisory_id
- severity
- cve_ids
- affected_versions
- fixed_versions
- published_utc

Allowed severity values:

- critical
- high
- medium
- low

## Publication rules

- Advisory is published after fix availability unless embargo is active.
- CVE references must be present when assigned.
- `published_utc` must be RFC3339 UTC (`YYYY-MM-DDTHH:MM:SSZ`).
- Empty `affected_versions` and `fixed_versions` lists are invalid.

## Tooling and gate wiring

- Lint tool: `tools/security_advisory_lint_v1.py`
- Sub-gate: `make test-vuln-response-v1`
- Parent gate: `make test-security-hardening-v3`
- CI step: `Vulnerability response v1 gate`

## Required tests

- `tests/security/test_vuln_response_docs_v1.py`
- `tests/security/test_advisory_schema_v1.py`
- `tests/security/test_vuln_response_gate_v1.py`
