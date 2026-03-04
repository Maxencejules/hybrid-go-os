# Update Signing Policy v1

Date: 2026-03-04  
Milestone: M14 Productization + Release Engineering v1  
Status: active release gate

## Purpose

Define signing-key handling policy for update metadata and client trust
verification.

## Key policy baseline

- Signing algorithm: `hmac-sha256` for current model-level lane.
- Active signing key is identified by `key_id`.
- Key rotation cadence: quarterly baseline or emergency rotation on compromise.
- A new key cannot sign updates until release + security owners approve.

## Client trust policy

- Clients verify:
  - metadata schema,
  - signature algorithm and key identity,
  - signature integrity,
  - monotonic build sequence,
  - metadata freshness (`expires_utc`).
- Compromised/retired keys are rejected once removed from trusted policy set.

## Incident response hooks

- Suspected key compromise triggers:
  - immediate key revocation,
  - forced key rotation,
  - emergency metadata release with higher sequence.
- Follow incident process in `docs/security/incident_response_v1.md`.

## Required release gates

- Local: `make test-release-engineering-v1`
- CI: `Release engineering v1 gate`
