# Security Fuzzing v1

Date: 2026-03-04  
Milestone: M10

## Goal

Run a continuous, machine-readable fuzz gate for security policy invariants and
track crash/violation SLA in CI artifacts.

## Harness

- Tool: `tools/run_security_fuzz_v1.py`
- Output: `out/security-fuzz-report.json`
- Schema: `rugo.security_fuzz_report.v1`

Report fields include:

- `seed_start`
- `cases`
- `iterations_per_case`
- `total_violations`
- `crash_sla_hours`

## CI policy

- Security gate fails if `total_violations != 0`.
- Fuzz report is uploaded as build artifact for triage continuity.

## Local run

```bash
python3 tools/run_security_fuzz_v1.py \
  --seed 20260304 \
  --iterations 2000 \
  --cases 4 \
  --out out/security-fuzz-report.json
```

## Executable checks

- `tests/security/test_security_fuzz_harness_v1.py`
