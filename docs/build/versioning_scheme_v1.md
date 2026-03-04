# Versioning Scheme v1

Date: 2026-03-04  
Milestone: M14 Productization + Release Engineering v1  
Status: active release gate

## Purpose

Define the version syntax and monotonic sequencing rules used by release and
update tooling.

## Version format

- Core format: `MAJOR.MINOR.PATCH`
- Pre-release suffix (optional):
  - `-beta.N`
  - `-nightly.YYYYMMDD`
- Build metadata suffix (optional):
  - `+build.<sequence>`

Examples:

- `1.0.0`
- `1.1.0-beta.2`
- `1.1.0-nightly.20260304+build.120`

## Compatibility semantics

- MAJOR: backward-incompatible contract change.
- MINOR: additive backward-compatible capability.
- PATCH: bugfix or hardening with no contract expansion.

## Monotonic update sequencing

- Every published update metadata set carries:
  - `version`,
  - `build_sequence` (strictly increasing integer),
  - `created_utc`.
- Clients reject metadata with a lower or equal `build_sequence` than last
  trusted state for the same channel.
- Channel switches (nightly -> beta -> stable) are explicit policy decisions
  and do not bypass monotonic checks within each channel.

## Deprecation timing

- A deprecation notice must appear at least one MINOR release before removal.
- Removals require MAJOR release unless security emergency policy is invoked.
