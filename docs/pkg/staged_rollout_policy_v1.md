# Staged Rollout Policy v1

Status: draft  
Version: v1

## Rollout Stages

- canary
- small-batch
- broad

## Safety Rules

- Blast-radius budget is defined per stage.
- Stage promotion requires health and error-rate criteria.
- Failed criteria triggers automatic halt.

## Evidence

- Artifact schema: `rugo.canary_rollout_report.v1`.
- Gate: `test-fleet-rollout-safety-v1`.

