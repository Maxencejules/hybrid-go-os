# Canary SLO Policy v1

Status: draft  
Version: v1

## Objective

Define SLO-triggered halt and rollback criteria for staged rollouts.

## Policy

- Canary stage has explicit latency and error-rate SLOs.
- Exceeding threshold triggers automatic halt.
- Rollback decision and outcome are recorded as release artifacts.

## Evidence

- Artifact schema: `rugo.rollout_abort_drill_report.v1`.
- Gate: `test-fleet-rollout-safety-v1`.

