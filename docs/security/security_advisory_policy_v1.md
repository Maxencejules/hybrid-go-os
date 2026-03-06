# Security Advisory Policy v1

Status: draft  
Version: v1

## Advisory Schema

Required fields:

- advisory_id
- severity
- cve_ids
- affected_versions
- fixed_versions
- published_utc

## Publication Rules

- Advisory is published after fix availability unless embargo is active.
- CVE references must be present when assigned.

## Evidence

- Lint artifact schema: `rugo.security_advisory_lint_report.v1`.
- Gate: `test-vuln-response-v1`.

