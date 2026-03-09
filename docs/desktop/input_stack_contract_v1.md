# Input Stack Contract v1

Date: 2026-03-09  
Milestone: M35 Desktop + Interactive UX Baseline v1  
Status: active release gate

## Objective

Define deterministic keyboard and pointer baseline behavior for interactive
desktop sessions.

## Contract identifiers

- Input stack contract ID: `rugo.input_stack_contract.v1`
- Parent desktop profile ID: `rugo.desktop_profile.v1`
- Input baseline report schema: `rugo.desktop_smoke_report.v1`

## Required input checks

- `input_keyboard_latency`
  - keyboard event p95 latency must be `<= 12 ms`.
- `input_pointer_latency`
  - pointer move/click event p95 latency must be `<= 14 ms`.
- `input_focus_delivery`
  - focused window must receive keyboard and pointer events reliably.
- `input_repeat_consistency`
  - deterministic key repeat and pointer stream sequencing is required.

## Reliability thresholds

- input delivery success ratio must be `>= 0.995`
- dropped input events must be `<= 2` for baseline campaign

## Tooling and gate wiring

- Smoke runner: `tools/run_desktop_smoke_v1.py`
- Local desktop gate: `make test-desktop-stack-v1`
- CI desktop gate: `Desktop stack v1 gate`

