"""M35 PR-2: display/session smoke checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_desktop_smoke_v1 as smoke  # noqa: E402


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def _check(data: dict, check_id: str) -> dict:
    matches = [entry for entry in data["checks"] if entry["check_id"] == check_id]
    assert len(matches) == 1
    return matches[0]


def test_display_session_smoke_v1_deterministic_report():
    first = smoke.run_smoke(seed=20260309)
    second = smoke.run_smoke(seed=20260309)
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_display_session_smoke_v1_schema_and_pass(tmp_path: Path):
    out = tmp_path / "desktop-smoke-v1.json"
    rc = smoke.main(["--seed", "20260309", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.desktop_smoke_report.v1"
    assert data["policy_id"] == "rugo.desktop_profile.v1"
    assert data["display_contract_id"] == "rugo.display_stack_contract.v1"
    assert data["gate_pass"] is True
    assert data["total_failures"] == 0
    assert data["summary"]["display"]["pass"] is True
    assert data["summary"]["session"]["pass"] is True
    assert _check(data, "display_mode_set")["pass"] is True
    assert _check(data, "session_desktop_ready")["pass"] is True


def test_display_session_smoke_v1_detects_display_failure(tmp_path: Path):
    out = tmp_path / "desktop-smoke-v1-fail.json"
    rc = smoke.main(
        [
            "--inject-failure",
            "display_mode_set",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["total_failures"] >= 1
    assert data["summary"]["display"]["failures"] >= 1
    failed = _check(data, "display_mode_set")
    assert failed["pass"] is False

