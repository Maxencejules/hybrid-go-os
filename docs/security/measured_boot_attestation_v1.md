# Measured Boot Attestation v1

Status: draft  
Version: v1

## Objective

Define measured-boot attestation contract for release evidence.

## Contract

- TPM event log is exported and machine-readable.
- PCR set must include `0,2,4,7` unless profile documents an exception.
- Policy verdict must be explicit: pass/fail with reason list.

## Evidence

- Artifact schema: `rugo.measured_boot_report.v1`.
- Tests: `tests/hw/test_measured_boot_attestation_v1.py`, `tests/hw/test_tpm_eventlog_schema_v1.py`.

