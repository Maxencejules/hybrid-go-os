# Secure Boot Policy v1

Date: 2026-03-04  
Milestone: M10

## Goal

Establish a verifiable boot artifact trust chain with deterministic rejection of
tampered artifacts.

## Manifest contract

Boot artifacts are signed through `tools/secure_boot_manifest_v1.py`.

Manifest schema:

- `schema`: `rugo.secure_boot_manifest.v1`
- `key_id`: signing key identifier
- `created_utc`: signing timestamp
- `artifacts[]`:
  - `path` (relative path)
  - `sha256`
  - `size`
- `signature`:
  - `alg`: `hmac-sha256`
  - `value`: HMAC signature over canonical payload JSON

## Validation policy

Verification must fail if any of the following occurs:

- schema mismatch,
- signature mismatch,
- artifact missing,
- artifact size mismatch,
- artifact hash mismatch.

## Key rotation procedure

1. Introduce new signing key material and new `key_id`.
2. Sign fresh manifests with the new key.
3. Verify manifests with the new key in CI gate.
4. Remove old key from trusted CI secrets after transition window.

M10 baseline tests include explicit key rotation behavior validation.

## CLI workflow

Sign:

```bash
python3 tools/secure_boot_manifest_v1.py sign \
  --key "$BOOT_KEY" \
  --key-id "boot-key-2026-03" \
  --base-dir . \
  --out out/boot-manifest-v1.json \
  --artifacts out/kernel.elf out/os.iso
```

Verify:

```bash
python3 tools/secure_boot_manifest_v1.py verify \
  --key "$BOOT_KEY" \
  --base-dir . \
  --manifest out/boot-manifest-v1.json
```

## Executable checks

- `tests/security/test_secure_boot_manifest_v1.py`
