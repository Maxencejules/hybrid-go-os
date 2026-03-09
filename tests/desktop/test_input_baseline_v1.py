"""M35 PR-2: input baseline smoke checks."""

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


def test_input_baseline_v1_schema_and_pass(tmp_path: Path):
    out = tmp_path / "desktop-smoke-v1-input.json"
    rc = smoke.main(["--seed", "20260309", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.desktop_smoke_report.v1"
    assert data["input_contract_id"] == "rugo.input_stack_contract.v1"
    assert data["summary"]["input"]["pass"] is True
    assert data["input"]["checks_pass"] is True
    assert data["input"]["keyboard_latency_p95_ms"] <= 12
    assert data["input"]["pointer_latency_p95_ms"] <= 14
    assert data["input"]["input_delivery_ratio"] >= 0.995
    assert _check(data, "input_keyboard_latency")["pass"] is True
    assert _check(data, "input_pointer_latency")["pass"] is True


def test_input_baseline_v1_detects_keyboard_latency_regression(tmp_path: Path):
    out = tmp_path / "desktop-smoke-v1-input-fail.json"
    rc = smoke.main(
        [
            "--inject-failure",
            "input_keyboard_latency",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["input"]["failures"] >= 1
    assert _check(data, "input_keyboard_latency")["pass"] is False


def test_input_baseline_v1_rejects_unknown_check_id(tmp_path: Path):
    out = tmp_path / "desktop-smoke-v1-input-error.json"
    rc = smoke.main(
        [
            "--inject-failure",
            "input_nonexistent_check",
            "--out",
            str(out),
        ]
    )
    assert rc == 2
    assert not out.exists()

