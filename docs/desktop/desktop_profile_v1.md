# Desktop Profile v1

Date: 2026-03-09  
Milestone: M35 Desktop + Interactive UX Baseline v1  
Status: active release gate

## Objective

Define the bounded desktop and GUI compatibility baseline claimed by M35.

## Profile identifiers

- Desktop profile ID: `rugo.desktop_profile.v1`
- Desktop smoke schema: `rugo.desktop_smoke_report.v1`
- GUI app matrix schema: `rugo.gui_app_matrix_report.v1`
- GUI app tier schema: `rugo.gui_app_tiers.v1`

## Boundaries

In scope:
- single-seat desktop session bring-up
- baseline keyboard and pointer input
- bounded GUI app classes listed below

Out of scope:
- universal GPU/compositor parity claims
- broad claim of compatibility beyond declared tiers

## GUI baseline tiers

| Class | Tier | Minimum eligible cases | Minimum pass rate |
|---|---|---:|---:|
| `productivity` | `tier_productivity` | 6 | 0.83 |
| `media` | `tier_media` | 4 | 0.75 |
| `utility` | `tier_utility` | 5 | 0.80 |

## Gate requirements

- Desktop stack gate command:
  - `python tools/run_desktop_smoke_v1.py --out out/desktop-smoke-v1.json`
- GUI app matrix command:
  - `python tools/run_gui_app_matrix_v1.py --out out/gui-app-matrix-v1.json`
- Local gate: `make test-desktop-stack-v1`
- Local sub-gate: `make test-gui-app-compat-v1`
- CI gate: `Desktop stack v1 gate`
- CI sub-gate: `GUI app compatibility v1 gate`

Gate pass requires:

- desktop smoke `total_failures = 0`
- GUI app matrix `gate_pass = true`
- GUI app matrix `issues = []`

