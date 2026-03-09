# Window Manager Contract v1

Date: 2026-03-09  
Milestone: M35 Desktop + Interactive UX Baseline v1  
Status: active release gate

## Objective

Define deterministic window lifecycle behavior for the bounded desktop profile.

## Contract identifiers

- Window manager contract ID: `rugo.window_manager_contract.v1`
- Parent desktop profile ID: `rugo.desktop_profile.v1`
- Smoke report schema: `rugo.desktop_smoke_report.v1`

## Lifecycle contract

The baseline lifecycle is:

1. `window_create_ok`
2. `window_map_ok`
3. `window_focus_switch`
4. `window_close_ok`

Each lifecycle phase must emit a pass/fail check in the desktop smoke report.

## Required thresholds

- window create latency: `<= 80 ms`
- window map latency: `<= 55 ms`
- focus switch latency: `<= 40 ms`
- window close latency: `<= 35 ms`

## Failure policy

- Any lifecycle phase failure is release-blocking.
- Session remains declared healthy only when all lifecycle checks pass.
- Partial lifecycle success does not satisfy gate requirements.

## Tooling and gate wiring

- Smoke runner: `tools/run_desktop_smoke_v1.py`
- Local desktop gate: `make test-desktop-stack-v1`
- CI desktop gate: `Desktop stack v1 gate`
