# Font/Text Rendering Policy v1

Date: 2026-03-11  
Milestone: M51 GUI Runtime + Toolkit Bridge v1  
Status: active release gate

## Objective

Define the bounded text and font behavior the first GUI runtime and toolkit
bridge may claim without overreaching into broader shaping or international text
support.

## Policy identifiers

- Font/text rendering policy ID: `rugo.font_text_rendering_policy.v1`.
- Parent GUI runtime contract ID: `rugo.gui_runtime_contract.v1`.
- Runtime report schema: `rugo.gui_runtime_report.v1`.
- Toolkit compatibility schema: `rugo.toolkit_compat_report.v1`.
- Toolkit profile ID: `rugo.toolkit_profile.v1`.

## Declared text profile

- Default font family: `rugo-sans`.
- Fallback font family: `rugo-mono`.
- Declared shaping profile: `ascii-plus-latin-1-no-complex-shaping`.
- Raster mode: `grayscale-atlas`.
- Subpixel mode: `disabled`.
- Baseline grid: `4 px`.

## Required checks

- `text_glyph_cache_integrity`:
  - missing glyph count must remain `= 0`.
- `font_fallback_integrity`:
  - font fallback violations must remain `= 0`.
- `baseline_grid_alignment`:
  - baseline-grid violations must remain `= 0`.

## Reporting requirements

- `out/gui-runtime-v1.json` must expose:
  - `font_text.policy_id`
  - `font_text.default_font_family`
  - `font_text.fallback_font_family`
  - `font_text.shaping_profile`
  - `font_text.glyph_cache_entries`
  - `font_text.fallback_events`
  - `font_text.text_samples`
- Text evidence must remain tied to the corresponding
  `rugo.gui_runtime_report.v1` digest before it can claim `gate_pass=true`.

## Release gating

- Local gate: `make test-gui-runtime-v1`.
- Local sub-gate: `make test-toolkit-compat-v1`.
- CI gate: `GUI runtime v1 gate`.
- CI sub-gate: `Toolkit compatibility v1 gate`.
