"""M42 PR-2: deterministic cgroup baseline checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_isolation_campaign_v1 as isolation  # noqa: E402


def _check(data: dict, check_id: str) -> dict:
    rows = [entry for entry in data["checks"] if entry["check_id"] == check_id]
    assert len(rows) == 1
    return rows[0]


def test_cgroup_baseline_checks_pass_in_campaign():
    report = isolation.run_campaign(seed=20260310)
    assert report["summary"]["cgroup"]["pass"] is True
    assert report["cgroup"]["cpu_quota_enforcement_ratio"] == 1.0
    assert report["cgroup"]["memory_limit_enforcement_ratio"] == 1.0
    assert report["cgroup"]["io_weight_enforcement_ratio"] == 1.0
    assert report["cgroup"]["pids_limit_enforcement_ratio"] == 1.0
    assert _check(report, "cgroup_cpu_quota_enforcement_ratio")["pass"] is True
    assert _check(report, "cgroup_memory_limit_enforcement_ratio")["pass"] is True


def test_cgroup_baseline_detects_memory_limit_regression(tmp_path: Path):
    out = tmp_path / "isolation-campaign-v1-cgroup-fail.json"
    rc = isolation.main(
        [
            "--inject-failure",
            "cgroup_memory_limit_enforcement_ratio",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["cgroup"]["failures"] >= 1
    assert _check(data, "cgroup_memory_limit_enforcement_ratio")["pass"] is False
