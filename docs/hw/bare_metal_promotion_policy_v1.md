# Bare-Metal Promotion Policy v1

Date: 2026-03-09  
Milestone: M37 Hardware Breadth + Driver Matrix v4  
Lane: Rugo (Rust kernel + Go user space)  
Status: active promotion policy

## Purpose

Define deterministic promotion criteria for moving bare-metal candidate profiles
from evidence-only status to release-claimable support under matrix v4.

## Policy identity

- Policy identifier: `rugo.hw_baremetal_promotion_policy.v1`.
- Report schema: `rugo.hw_baremetal_promotion_report.v1`.
- Matrix evidence schema: `rugo.hw_matrix_evidence.v4`.

## Promotion thresholds

- Minimum consecutive green runs: `12`.
- Minimum campaign pass rate: `0.98`.
- Maximum tolerated fatal lifecycle errors: `0`.
- Maximum tolerated deterministic negative-path violations: `0`.

Promotion remains manual even when thresholds pass.

## Required evidence bundle

- `out/pytest-hw-matrix-v4.xml`
- `out/hw-matrix-v4.json`
- `out/hw-promotion-v1.json`
- hardware profile metadata (board ID, firmware revision, NIC/storage class)

## Policy checks

- Campaign duration must be greater than or equal to consecutive-run threshold.
- Trailing consecutive green runs must meet threshold.
- Campaign pass rate must meet threshold.
- Required evidence bundle must be complete.

## Gate wiring

- Matrix gate command:
  - `python tools/run_hw_matrix_v4.py --out out/hw-matrix-v4.json`
- Promotion evidence command:
  - `python tools/collect_hw_promotion_evidence_v1.py --out out/hw-promotion-v1.json`
- Local gate: `make test-hw-matrix-v4`.
- Local sub-gate: `make test-hw-baremetal-promotion-v1`.
- CI gate: `Hardware matrix v4 gate`.
- CI sub-gate: `Hardware bare-metal promotion v1 gate`.

## Failure handling

- Any failed policy check blocks promotion and requires explicit remediation
  evidence.
- A policy failure does not create an implicit support commitment.
- Promotion evidence is invalid if schema/version identifiers drift from policy
  declarations.
