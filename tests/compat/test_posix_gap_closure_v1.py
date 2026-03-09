"""M36 PR-2: deterministic POSIX gap closure report checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_posix_gap_report_v1 as gap  # noqa: E402


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def _required_row(data: dict, surface: str) -> dict:
    rows = [entry for entry in data["required_surfaces"] if entry["surface"] == surface]
    assert len(rows) == 1
    return rows[0]


def _deferred_row(data: dict, surface: str) -> dict:
    rows = [entry for entry in data["deferred_surfaces"] if entry["surface"] == surface]
    assert len(rows) == 1
    return rows[0]


def test_posix_gap_report_v1_is_seed_deterministic():
    first = gap.run_report(seed=20260309)
    second = gap.run_report(seed=20260309)
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_posix_gap_report_v1_schema_and_gate_pass(tmp_path: Path):
    out = tmp_path / "posix-gap-report-v1.json"
    rc = gap.main(["--seed", "20260309", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.posix_gap_report.v1"
    assert data["profile_id"] == "rugo.compat_profile.v4"
    assert data["gate_pass"] is True
    assert data["total_failures"] == 0
    assert data["missing_required"] == []
    assert data["deferred_violations"] == []
    assert _required_row(data, "waitid")["status"] == "implemented"
    assert _required_row(data, "sendmsg")["status"] == "implemented"
    assert _deferred_row(data, "fork")["deterministic_error"] == "ENOSYS"
    assert _deferred_row(data, "epoll")["deterministic_error"] == "ENOSYS"


def test_posix_gap_report_v1_detects_missing_required_surface(tmp_path: Path):
    out = tmp_path / "posix-gap-report-v1-missing.json"
    rc = gap.main(
        [
            "--inject-missing-required",
            "waitid",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert "waitid" in data["missing_required"]
    reasons = {item["reason"] for item in data["issues"]}
    assert "missing_required" in reasons


def test_posix_gap_report_v1_detects_deferred_behavior_violation(tmp_path: Path):
    out = tmp_path / "posix-gap-report-v1-deferred.json"
    rc = gap.main(
        [
            "--inject-deferred-violation",
            "epoll",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert "epoll" in data["deferred_violations"]
    row = _deferred_row(data, "epoll")
    assert row["deterministic"] is False
    assert row["deterministic_error"] != "ENOSYS"


def test_posix_gap_report_v1_rejects_unknown_required_injection(tmp_path: Path):
    out = tmp_path / "posix-gap-report-v1-error.json"
    rc = gap.main(
        [
            "--inject-missing-required",
            "unknown_surface",
            "--out",
            str(out),
        ]
    )
    assert rc == 2
    assert not out.exists()
