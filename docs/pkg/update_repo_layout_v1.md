# Update Repository Layout v1

Date: 2026-03-04  
Milestone: M14 Productization + Release Engineering v1  
Status: active release gate

## Purpose

Freeze the on-disk repository layout used by update signing and client
verification tools.

## Directory structure

```text
<repo>/
  targets/
    system-image-<version>.bin
    ...
  metadata/
    update-metadata-v1.json
```

## Constraints

- `targets/` contains immutable content-addressed release targets.
- `metadata/update-metadata-v1.json` describes target digests/sizes and is
  signed.
- Target names are stable and deterministic for a given release version.
- Repository updates must be append-only at policy level; replaced target
  content requires a new version and sequence.

## Operational notes

- Local validation:
  - `python tools/update_client_verify_v1.py --repo out/update-repo-v1 --expect-version 1.0.0`
- Attack simulation:
  - `python tools/run_update_attack_suite_v1.py --seed 20260304 --out out/update-attack-suite-v1.json`
