"""M42 PR-2: deterministic namespace baseline checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_isolation_campaign_v1 as isolation  # noqa: E402


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def _check(data: dict, check_id: str) -> dict:
    rows = [entry for entry in data["checks"] if entry["check_id"] == check_id]
    assert len(rows) == 1
    return rows[0]


def test_namespace_campaign_v1_is_seed_deterministic():
    first = isolation.run_campaign(seed=20260310)
    second = isolation.run_campaign(seed=20260310)
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_namespace_campaign_v1_schema_and_pass(tmp_path: Path):
    out = tmp_path / "isolation-campaign-v1-namespace.json"
    rc = isolation.main(["--seed", "20260310", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.isolation_campaign_report.v1"
    assert data["isolation_profile_id"] == "rugo.isolation_profile.v1"
    assert data["gate_pass"] is True
    assert data["summary"]["namespace"]["pass"] is True
    assert data["namespace"]["checks_pass"] is True
    assert data["namespace"]["pid_isolation_ratio"] == 1.0
    assert data["namespace"]["mount_isolation_ratio"] == 1.0
    assert _check(data, "namespace_pid_isolation_ratio")["pass"] is True
    assert _check(data, "namespace_mount_isolation_ratio")["pass"] is True
    assert _check(data, "namespace_uts_isolation_ratio")["pass"] is True


def test_namespace_campaign_v1_detects_mount_isolation_regression(tmp_path: Path):
    out = tmp_path / "isolation-campaign-v1-namespace-fail.json"
    rc = isolation.main(
        [
            "--inject-failure",
            "namespace_mount_isolation_ratio",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["namespace"]["failures"] >= 1
    assert _check(data, "namespace_mount_isolation_ratio")["pass"] is False


def test_namespace_campaign_v1_rejects_unknown_check_id(tmp_path: Path):
    out = tmp_path / "isolation-campaign-v1-namespace-error.json"
    rc = isolation.main(
        [
            "--inject-failure",
            "namespace_nonexistent_check",
            "--out",
            str(out),
        ]
    )
    assert rc == 2
    assert not out.exists()
