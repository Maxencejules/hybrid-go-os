"""M51 PR-2: deterministic toolkit/event-loop checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_toolkit_compat_v1 as compat  # noqa: E402


def _out_path(name: str) -> Path:
    path = ROOT / "out" / "pytest-m51" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    return path


def test_toolkit_compat_v1_schema_profiles_and_event_loop():
    out = _out_path("toolkit-compat-v1.json")
    rc = compat.main(["--seed", "20260311", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    profiles = data["profiles"]

    assert data["schema"] == "rugo.toolkit_compat_report.v1"
    assert data["profile_id"] == "rugo.toolkit_profile.v1"
    assert data["runtime_schema"] == "rugo.gui_runtime_report.v1"
    assert data["gate"] == "test-toolkit-compat-v1"
    assert data["parent_gate"] == "test-gui-runtime-v1"
    assert data["gate_pass"] is True
    assert data["total_failures"] == 0

    assert profiles["rugo.widgets.retain.v1"]["eligible"] == 3
    assert profiles["rugo.widgets.retain.v1"]["passed"] == 3
    assert profiles["rugo.widgets.retain.v1"]["meets_threshold"] is True
    assert profiles["rugo.canvas.overlay.v1"]["eligible"] == 1
    assert profiles["rugo.canvas.overlay.v1"]["passed"] == 1
    assert profiles["rugo.canvas.overlay.v1"]["meets_threshold"] is True

    retain_loop = data["event_loop_profiles"]["rugo.widgets.retain.v1"]
    overlay_loop = data["event_loop_profiles"]["rugo.canvas.overlay.v1"]
    assert retain_loop["dispatch_model"] == "single-ui-thread-plus-runtime-queue"
    assert retain_loop["callback_order"] == ["input", "layout", "paint", "present"]
    assert overlay_loop["dispatch_model"] == "timer-plus-paint"
    assert overlay_loop["callback_order"] == ["timer", "paint", "present"]


def test_toolkit_compat_v1_detects_event_loop_regression():
    out = _out_path("toolkit-compat-v1-event-loop-fail.json")
    rc = compat.main(
        [
            "--inject-event-loop-failure",
            "settings.panel",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["profiles"]["rugo.widgets.retain.v1"]["meets_threshold"] is False
    assert any(issue["reason"] == "event_loop_failure" for issue in data["issues"])
