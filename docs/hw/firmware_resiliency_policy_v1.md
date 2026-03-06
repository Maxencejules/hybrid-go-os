# Firmware Resiliency Policy v1

Status: draft  
Version: v1

## Scope

Defines protect/detect/recover expectations for firmware and boot-path integrity on supported hardware tiers.

## Policy

- Protect: signed firmware update path and immutable trust anchor handling.
- Detect: measured boot evidence must be captured for each release candidate.
- Recover: documented recovery procedure for failed or tampered firmware state.

## Evidence

- Artifact schema: `rugo.measured_boot_report.v1`.
- Gate: `test-firmware-attestation-v1`.

