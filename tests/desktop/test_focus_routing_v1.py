"""M49 PR-2: deterministic focus routing checks."""

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


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def test_focus_routing_v1_deterministic_report():
    first = runtime.run_input_seat_runtime(seed=20260311)
    second = runtime.run_input_seat_runtime(seed=20260311)
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_focus_routing_v1_schema_and_policy():
    out = _out_path("input-seat-v1-focus.json")
    rc = runtime.main(["--seed", "20260311", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    transitions = data["focus"]["transitions"]

    assert data["focus_policy_id"] == "rugo.focus_routing_policy.v1"
    assert data["focus"]["previous_focus_target"] == "desktop.shell.launcher"
    assert data["focus"]["keyboard_focus_target"] == "settings.panel"
    assert data["focus"]["pointer_focus_target"] == "settings.panel"
    assert len(transitions) == 1
    assert transitions[0]["from"] == "desktop.shell.launcher"
    assert transitions[0]["to"] == "settings.panel"
    assert transitions[0]["latency_ms"] <= 35.0
    assert data["focus"]["misroutes"] == 0
    assert data["seat"]["focus_owner_count"] == 1
    assert data["summary"]["focus"]["pass"] is True


def test_focus_routing_v1_detects_misroute_regression():
    out = _out_path("input-seat-v1-focus-fail.json")
    rc = runtime.main(
        [
            "--inject-failure",
            "focus_route_integrity",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert "focus_route_integrity" in data["failures"]
    assert data["summary"]["focus"]["failures"] >= 1
    assert data["focus"]["misroutes"] >= 1
    assert data["focus"]["checks_pass"] is False
