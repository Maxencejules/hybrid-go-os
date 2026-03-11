"""M49 PR-2: deterministic keyboard event delivery checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_input_seat_runtime_v1 as runtime  # noqa: E402


def _out_path(name: str) -> Path:
    path = ROOT / "out" / "pytest-m49" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    return path


def test_keyboard_event_delivery_v1_schema_and_pass():
    out = _out_path("input-seat-v1-keyboard.json")
    rc = runtime.main(["--seed", "20260311", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.input_seat_runtime_report.v1"
    assert data["contract_id"] == "rugo.seat_input_contract.v1"
    assert data["seat"]["seat_id"] == "seat0"
    assert data["keyboard"]["device_class"] == "usb-hid"
    assert data["keyboard"]["driver"] == "xhci-usb-hid"
    assert data["keyboard"]["delivery_ratio"] >= 0.999
    assert data["keyboard"]["repeat_jitter_p95_ms"] <= 3.0
    assert data["keyboard"]["target_surface"] == "settings.panel"
    assert data["summary"]["delivery"]["pass"] is True
    assert data["gate_pass"] is True


def test_keyboard_event_delivery_v1_detects_delivery_regression():
    out = _out_path("input-seat-v1-keyboard-fail.json")
    rc = runtime.main(
        [
            "--inject-failure",
            "keyboard_event_delivery",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert "keyboard_event_delivery" in data["failures"]
    assert data["summary"]["delivery"]["failures"] >= 1
    assert data["keyboard"]["checks_pass"] is False
