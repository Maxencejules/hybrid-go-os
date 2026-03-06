# Release Attestation Policy v1

Status: draft  
Version: v1

## Objective

Validate release attestation continuity across branches, channels, and support windows.

## Policy

- Each candidate must include a signed release attestation.
- Policy hash or profile ID drift must be detected.
- Drift beyond threshold is gate-blocking.

## Evidence

- Artifact schema: `rugo.release_attestation_verification.v1`.

