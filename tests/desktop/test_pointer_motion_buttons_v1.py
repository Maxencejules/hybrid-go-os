"""M49 PR-2: deterministic pointer motion/button event-path checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_hid_event_path_v1 as hid  # noqa: E402


def _out_path(name: str) -> Path:
    path = ROOT / "out" / "pytest-m49" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    return path


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    stable.pop("artifact_refs", None)
    return stable


def test_pointer_motion_buttons_v1_deterministic_event_path():
    first = _out_path("hid-event-path-v1-a.json")
    second = _out_path("hid-event-path-v1-b.json")

    assert hid.main(["--seed", "20260311", "--out", str(first)]) == 0
    assert hid.main(["--seed", "20260311", "--out", str(second)]) == 0

    first_data = json.loads(first.read_text(encoding="utf-8"))
    second_data = json.loads(second.read_text(encoding="utf-8"))
    assert _strip_timestamp(first_data) == _strip_timestamp(second_data)


def test_pointer_motion_buttons_v1_schema_and_phases():
    out = _out_path("hid-event-path-v1-pointer.json")
    rc = hid.main(["--seed", "20260311", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    phases = [event["phase"] for event in data["event_stream"]]

    assert data["schema"] == "rugo.hid_event_path_report.v1"
    assert data["active_display_path"] == "virtio-gpu-pci"
    assert "pointer_motion" in phases
    assert "button_down" in phases
    assert "button_up" in phases
    assert data["pointer_path"]["motion_latency_p95_ms"] <= 10.0
    assert data["pointer_path"]["button_latency_p95_ms"] <= 12.0
    assert data["pointer_path"]["path_checks_pass"] is True
    assert data["gate_pass"] is True


def test_pointer_motion_buttons_v1_detects_button_regression():
    out = _out_path("hid-event-path-v1-pointer-fail.json")
    rc = hid.main(
        [
            "--inject-runtime-failure",
            "pointer_button_delivery",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert "pointer_button_delivery" in data["runtime_failures"]
    assert data["pointer_path"]["path_checks_pass"] is False
