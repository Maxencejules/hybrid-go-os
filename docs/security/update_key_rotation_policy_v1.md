# Update Key Rotation Policy v1

Status: draft  
Version: v1

## Objective

Define trust-root and signing-key rotation process for update metadata.

## Policy

- Rotation must support overlap window for old/new keys.
- Emergency revoke path is documented and drill-tested.
- Clients must reject metadata from revoked keys after cutoff.

## Evidence

- Artifact schema: `rugo.update_key_rotation_drill.v1`.
- Gate coverage: `test-update-trust-v1`.

