"""M51 PR-2: deterministic font/text rendering checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_gui_runtime_v1 as runtime  # noqa: E402


def _out_path(name: str) -> Path:
    path = ROOT / "out" / "pytest-m51" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    return path


def test_font_text_rendering_v1_schema_and_policy_fields():
    out = _out_path("gui-runtime-v1-fonts.json")
    rc = runtime.main(["--seed", "20260311", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    font_text = data["font_text"]

    assert font_text["policy_id"] == "rugo.font_text_rendering_policy.v1"
    assert font_text["default_font_family"] == "rugo-sans"
    assert font_text["fallback_font_family"] == "rugo-mono"
    assert font_text["shaping_profile"] == "ascii-plus-latin-1-no-complex-shaping"
    assert font_text["raster_mode"] == "grayscale-atlas"
    assert font_text["subpixel_mode"] == "disabled"
    assert font_text["baseline_grid_px"] == 4
    assert font_text["glyph_cache_entries"] >= 164
    assert font_text["atlas_pages"] == 1
    assert font_text["missing_glyph_count"] == 0
    assert font_text["font_fallback_violation_count"] == 0
    assert font_text["baseline_grid_violation_count"] == 0
    assert font_text["fallback_events"] == 1
    assert any(sample["font_family"] == "rugo-mono" for sample in font_text["text_samples"])
    assert font_text["checks_pass"] is True
    assert data["summary"]["text"]["pass"] is True


def test_font_text_rendering_v1_detects_fallback_regression():
    out = _out_path("gui-runtime-v1-fonts-fail.json")
    rc = runtime.main(
        [
            "--inject-failure",
            "font_fallback_integrity",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert "font_fallback_integrity" in data["failures"]
    assert data["summary"]["text"]["failures"] >= 1
    assert data["font_text"]["checks_pass"] is False
