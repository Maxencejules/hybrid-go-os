# Security Threat Model v2

Date: 2026-03-09  
Milestone: M28 Security Hardening Program v3  
Status: active release gate contract

## Purpose

Document the v2 threat model used by the M28 hardening profile and bind threat
classes to executable enforcement.

## Contract identifiers

- Threat model ID: `rugo.security_threat_model.v2`
- Hardening profile linkage: `rugo.security_hardening_profile.v3`
- Attack suite schema: `rugo.security_attack_suite_report.v3`
- Fuzz schema: `rugo.security_fuzz_report.v2`

## Assets in scope

- Kernel syscall boundary and policy enforcement.
- Capability and handle-rights state.
- Security advisory records and CVE linkage.
- Vulnerability intake, triage, and embargo workflow state.

## Adversary classes

- External attacker attempting syscall policy bypass or privilege escalation.
- Supply-chain attacker attempting unsigned/incomplete advisory publication.
- Process attacker attempting rights escalation through descriptor misuse.
- Disclosure attacker attempting premature embargo leakage.

## Primary attack scenarios

- Attack scenario `syscall_filter_bypass`: unapproved syscall path execution.
- Attack scenario `capability_rights_escalation`: rights amplification attempt.
- Attack scenario `unsigned_advisory_publish`: advisory accepted without schema
  and CVE requirements.
- Attack scenario `embargo_breach`: workflow success despite failed embargo
  stage.
- Attack scenario `stale_triage_ticket`: triage closure exceeds policy window.

## Severity and closure policy

- Severity classes: `critical`, `high`, `medium`, `low`.
- Triage SLA hours: `24`.
- Severity assignment SLA hours: `72`.
- Maximum closure SLA hours: `120`.
- Release gate threshold: `total_failures == 0` and `total_violations == 0`.

## Evidence mapping

- Attack scenario coverage: `tools/run_security_attack_suite_v3.py`
- Fuzz and policy invariant coverage: `tools/run_security_fuzz_v2.py`
- Advisory schema coverage: `tools/security_advisory_lint_v1.py`
- Embargo workflow coverage: `tools/security_embargo_drill_v1.py`

## Required tests

- `tests/security/test_attack_suite_v3.py`
- `tests/security/test_fuzz_gate_v2.py`
- `tests/security/test_policy_enforcement_v3.py`
- `tests/security/test_security_hardening_gate_v3.py`
