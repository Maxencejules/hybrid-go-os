# Toolkit Profile v1

Date: 2026-03-11  
Milestone: M51 GUI Runtime + Toolkit Bridge v1  
Status: active release gate

## Objective

Freeze the bounded toolkit-facing profile that the first in-tree GUI runtime is
allowed to claim.

## Profile identifiers

- Toolkit profile ID: `rugo.toolkit_profile.v1`.
- Parent GUI runtime contract ID: `rugo.gui_runtime_contract.v1`.
- Runtime report schema: `rugo.gui_runtime_report.v1`.
- Toolkit compatibility schema: `rugo.toolkit_compat_report.v1`.
- Font/text rendering policy ID: `rugo.font_text_rendering_policy.v1`.

## Declared profiles

- Declared retained profile: `rugo.widgets.retain.v1`.
  - render model: `retained-scene`
  - event model: `single-ui-thread-plus-runtime-queue`
  - supported primitives: `label`, `button`, `text_field`, `scroll_view`, `panel`
- Declared overlay profile: `rugo.canvas.overlay.v1`.
  - render model: `immediate-overlay`
  - event model: `timer-plus-paint`
  - supported primitives: `toast`, `icon`, `label`, `panel`

## Compatibility thresholds

- `rugo.widgets.retain.v1`:
  - minimum compatible cases: `3`
  - minimum pass rate: `1.0`
- `rugo.canvas.overlay.v1`:
  - minimum compatible cases: `1`
  - minimum pass rate: `1.0`

## Required reporting

- `out/toolkit-compat-v1.json` must expose:
  - `profiles`
  - `cases`
  - `event_loop_profiles`
  - `source_reports`
  - `digest`
- Every compatibility case must include:
  - `case_id`
  - `profile`
  - `launch_ok`
  - `render_ok`
  - `text_ok`
  - `event_loop_ok`
  - `passed`

## Release gating

- Local gate: `make test-gui-runtime-v1`.
- Local sub-gate: `make test-toolkit-compat-v1`.
- CI gate: `GUI runtime v1 gate`.
- CI sub-gate: `Toolkit compatibility v1 gate`.
