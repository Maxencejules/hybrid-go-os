# Incident Response and Security Advisory Process v1

Date: 2026-03-04  
Milestone: M10

## Scope

Define minimum response workflow for security findings in kernel, build chain,
and package/bootstrap tooling.

## Intake channels

- Private maintainer disclosure channel (preferred for embargoed reports).
- Public issue tracker for non-sensitive defects.

## Severity classes

- `S0`: active exploitation or trust-chain compromise.
- `S1`: privilege boundary bypass or deterministic memory safety break.
- `S2`: security hardening regression without known exploitation path.
- `S3`: low-impact defensive gap/documentation issue.

## SLA targets

- `S0`: triage in 4h, mitigation plan in 24h.
- `S1`: triage in 24h, fix plan in 72h.
- `S2`: triage in 3 business days.
- `S3`: triage in 7 business days.

M10 fuzz-report baseline tracks `crash_sla_hours = 24`.

## Advisory process

1. Assign incident ID and severity.
2. Capture reproducible evidence (logs, seed, commit, environment).
3. Land fix behind tests/regression gate.
4. Publish security advisory with:
   - impact summary,
   - affected versions/commits,
   - mitigation and upgrade path,
   - credit timeline.

## Required artifacts

- failing test or fuzz seed,
- fix commit hash,
- release note/advisory entry.

## References

- `tools/run_security_fuzz_v1.py`
- `tests/security/test_security_fuzz_harness_v1.py`
