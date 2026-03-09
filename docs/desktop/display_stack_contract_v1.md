# Display Stack Contract v1

Date: 2026-03-09  
Milestone: M35 Desktop + Interactive UX Baseline v1  
Status: active release gate

## Objective

Define deterministic display/session bring-up requirements for the declared
desktop baseline profile.

## Contract identifiers

- Display stack contract ID: `rugo.display_stack_contract.v1`
- Parent desktop profile ID: `rugo.desktop_profile.v1`
- Smoke report schema: `rugo.desktop_smoke_report.v1`

## Required bring-up checks

- `display_mode_set`:
  - desktop mode must be selected and framebuffer/compositor surface must be
    available.
  - threshold: mode set latency `<= 220 ms`.
- `display_scanout_stable`:
  - scanout pipeline must remain stable for baseline frame cadence checks.
  - threshold: frame-drop ratio `<= 0.01`.
- `session_handshake_ready`:
  - display server and session manager handshake must complete.
  - threshold: handshake latency `<= 120 ms`.
- `session_desktop_ready`:
  - baseline desktop shell must report ready and accept first client window.
  - threshold: desktop ready latency `<= 350 ms`.

## Determinism rules

- All display checks must be represented as machine-readable check entries in
  `out/desktop-smoke-v1.json`.
- Baseline gate pass requires `total_failures = 0`.
- Unsupported display acceleration features remain out of scope and must not be
  counted as pass criteria in this contract.

## Tooling and gate wiring

- Smoke runner: `tools/run_desktop_smoke_v1.py`
- Local desktop gate: `make test-desktop-stack-v1`
- CI desktop gate: `Desktop stack v1 gate`

