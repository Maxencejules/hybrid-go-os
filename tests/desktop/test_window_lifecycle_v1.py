"""M35 PR-2: window lifecycle smoke checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_desktop_smoke_v1 as smoke  # noqa: E402


def _check(data: dict, check_id: str) -> dict:
    matches = [entry for entry in data["checks"] if entry["check_id"] == check_id]
    assert len(matches) == 1
    return matches[0]


def test_window_lifecycle_v1_schema_and_pass(tmp_path: Path):
    out = tmp_path / "desktop-smoke-v1-window.json"
    rc = smoke.main(["--seed", "20260309", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.desktop_smoke_report.v1"
    assert data["window_contract_id"] == "rugo.window_manager_contract.v1"
    assert data["summary"]["window"]["pass"] is True
    assert data["window_lifecycle"]["checks_pass"] is True
    assert data["window_lifecycle"]["window_create_ms"] <= 80
    assert data["window_lifecycle"]["window_map_ms"] <= 55
    assert data["window_lifecycle"]["focus_switch_ms"] <= 40
    assert data["window_lifecycle"]["window_close_ms"] <= 35
    assert _check(data, "window_create_ok")["pass"] is True
    assert _check(data, "window_close_ok")["pass"] is True


def test_window_lifecycle_v1_detects_focus_switch_failure(tmp_path: Path):
    out = tmp_path / "desktop-smoke-v1-window-fail.json"
    rc = smoke.main(
        [
            "--inject-failure",
            "window_focus_switch",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["window"]["failures"] >= 1
    assert _check(data, "window_focus_switch")["pass"] is False

