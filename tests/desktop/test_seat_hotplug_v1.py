"""M49 PR-2: deterministic seat hotplug checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_hid_event_path_v1 as hid  # noqa: E402
import run_input_seat_runtime_v1 as runtime  # noqa: E402


def _out_path(name: str) -> Path:
    path = ROOT / "out" / "pytest-m49" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    return path


def test_seat_hotplug_v1_schema_and_pass():
    out = _out_path("input-seat-v1-hotplug.json")
    rc = runtime.main(["--seed", "20260311", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["hotplug"]["controller"] == "xhci"
    assert data["hotplug"]["rebind_latency_ms"] <= 120.0
    assert data["hotplug"]["dropped_events_during_rebind"] <= 1
    assert data["hotplug"]["focus_restored"] is True
    assert data["hotplug"]["checks_pass"] is True
    assert data["summary"]["seat"]["pass"] is True


def test_seat_hotplug_v1_event_path_contains_rebind():
    out = _out_path("hid-event-path-v1-hotplug.json")
    rc = hid.main(["--seed", "20260311", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    phases = [event["phase"] for event in data["event_stream"]]
    assert "device_detach" in phases
    assert "device_rebind" in phases
    assert data["hotplug_path"]["detach_and_rebind_present"] is True
    assert data["hotplug_path"]["path_checks_pass"] is True


def test_seat_hotplug_v1_detects_rebind_regression():
    out = _out_path("input-seat-v1-hotplug-fail.json")
    rc = runtime.main(
        [
            "--inject-failure",
            "seat_hotplug_rebind",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert "seat_hotplug_rebind" in data["failures"]
    assert data["summary"]["seat"]["failures"] >= 1
    assert data["hotplug"]["checks_pass"] is False
