# Update Trust Model v1

Status: draft  
Version: v1

## Threats Covered

- rollback
- replay/freeze
- metadata expiry bypass
- mix-and-match target metadata

## Requirements

- Metadata expiry is mandatory and validated.
- Monotonic build sequence is enforced.
- Target set and digest set must be bound to signed metadata.

## Evidence

- Artifact schema: `rugo.update_trust_report.v1`.
- Gate: `test-update-trust-v1`.

