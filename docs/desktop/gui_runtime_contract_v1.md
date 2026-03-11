# GUI Runtime Contract v1

Date: 2026-03-11  
Milestone: M51 GUI Runtime + Toolkit Bridge v1  
Status: active release gate

## Objective

Define the bounded GUI runtime that sits above the live window/input/display
stack and below the declared toolkit profiles for in-tree graphical apps.

## Contract identifiers

- GUI runtime contract ID: `rugo.gui_runtime_contract.v1`.
- Parent window system contract ID: `rugo.window_manager_contract.v2`.
- Parent seat contract ID: `rugo.seat_input_contract.v1`.
- Parent display runtime contract ID: `rugo.display_runtime_contract.v1`.
- Runtime report schema: `rugo.gui_runtime_report.v1`.
- Toolkit compatibility schema: `rugo.toolkit_compat_report.v1`.
- Toolkit profile ID: `rugo.toolkit_profile.v1`.
- Font/text rendering policy ID: `rugo.font_text_rendering_policy.v1`.

## Declared runtime boundary

- Declared runtime path:
  - window/runtime source schema: `rugo.window_system_runtime_report.v1`
  - event/input source schema: `rugo.input_seat_runtime_report.v1`
  - display source schema: `rugo.display_runtime_report.v1`
- Declared in-tree app set:
  - `desktop.shell.workspace`
  - `files.panel`
  - `settings.panel`
  - `toast.network`
- Declared toolkit profiles:
  - `rugo.widgets.retain.v1`
  - `rugo.canvas.overlay.v1`

## Required checks

- `app_launch_budget`:
  - app launch latency p95 must remain `<= 90 ms`.
- `launch_surface_bind_integrity`:
  - runtime app-to-surface mismatches must remain `= 0`.
- `first_frame_budget`:
  - first-frame latency p95 must remain `<= 50 ms`.
- `frame_present_budget`:
  - app frame latency p95 must remain `<= 16.667 ms`.
- `input_roundtrip_budget`:
  - focused app input round-trip latency p95 must remain `<= 22 ms`.
- `text_glyph_cache_integrity`:
  - missing glyph count must remain `= 0`.
- `font_fallback_integrity`:
  - invalid font fallback selections must remain `= 0`.
- `baseline_grid_alignment`:
  - baseline-grid violations must remain `= 0`.
- `event_loop_wakeup_budget`:
  - event-loop wakeup latency p95 must remain `<= 8 ms`.
- `event_queue_drain_budget`:
  - event queue drain latency p95 must remain `<= 12 ms`.
- `callback_order_integrity`:
  - callback reorders must remain `= 0`.

## Runtime reporting requirements

- `out/gui-runtime-v1.json` must expose:
  - `runtime_topology`
  - `apps`
  - `toolkit_profiles`
  - `font_text`
  - `event_loop`
  - `source_reports`
  - `digest`
- Every app record must include:
  - `app_id`
  - `window_id`
  - `surface_id`
  - `toolkit_profile`
  - `launch_ms`
  - `first_frame_ms`
  - `checks_pass`
- Runtime closure requires the focused app, retired overlay app, and selected
  toolkit profile set to be auditable from the same runtime report digest.

## Release gating

- Local gate: `make test-gui-runtime-v1`.
- Local sub-gate: `make test-toolkit-compat-v1`.
- CI gate: `GUI runtime v1 gate`.
- CI sub-gate: `Toolkit compatibility v1 gate`.
