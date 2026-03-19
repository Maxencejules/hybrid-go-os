"""X3 runtime-backed platform/ecosystem report checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_x3_platform_runtime_v1 as tool  # noqa: E402
import x3_platform_runtime_common_v1 as common  # noqa: E402


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def _out_path(name: str) -> Path:
    path = ROOT / "out" / "pytest-x3" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    return path


def _backlog(data: dict, backlog_id: str) -> dict:
    rows = [row for row in data["backlog_closure"] if row["backlog"] == backlog_id]
    assert len(rows) == 1
    return rows[0]


def test_x3_platform_runtime_report_is_seed_deterministic():
    capture = common.load_runtime_capture(fixture=True)
    reports = common.collect_source_reports(seed=20260318)
    first = common.build_report(seed=20260318, capture=capture, reports=reports)
    second = common.build_report(seed=20260318, capture=capture, reports=reports)
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_x3_platform_runtime_report_schema_and_backlog_closure():
    out = _out_path("x3-platform-runtime-v1.json")
    rc = tool.main(["--seed", "20260318", "--fixture", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.x3_platform_ecosystem_runtime_report.v1"
    assert data["track_id"] == "X3"
    assert data["policy_id"] == "rugo.x3_platform_ecosystem_runtime_qualification.v1"
    assert data["gate"] == "test-x3-platform-runtime-v1"
    assert data["capture"]["capture_mode"] == "fixture"
    assert data["gate_pass"] is True
    assert data["total_failures"] == 0
    assert data["summary"]["package_update"]["pass"] is True
    assert data["summary"]["storage_platform"]["pass"] is True
    assert data["summary"]["catalog_distribution"]["pass"] is True
    assert data["summary"]["backlogs"]["runtime_backed"] == 3
    assert data["summary"]["backlogs"]["total"] == 3

    for check_id in [
        "pkgsvc_lifecycle",
        "metadata_rotation",
        "catalog_distribution",
        "storage_platform",
        "pkgsvc_isolation",
    ]:
        assert any(check["check_id"] == check_id and check["pass"] is True for check in data["checks"])

    assert _backlog(data, "M26")["runtime_class"] == "Runtime-backed"
    assert _backlog(data, "M26")["status"] == "pass"
    assert _backlog(data, "M38")["status"] == "pass"
    assert _backlog(data, "M39")["status"] == "pass"


def test_x3_platform_runtime_report_detects_storage_regression():
    out = _out_path("x3-platform-runtime-v1-fail.json")
    rc = tool.main(
        [
            "--fixture",
            "--inject-failure",
            "storage_platform",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert "storage_platform" in data["failures"]
    assert _backlog(data, "M38")["status"] == "fail"


def test_x3_platform_runtime_report_rejects_unknown_check_id():
    out = _out_path("x3-platform-runtime-v1-error.json")
    rc = tool.main(["--inject-failure", "x3_nonexistent_check", "--out", str(out)])
    assert rc == 2
    assert not out.exists()
