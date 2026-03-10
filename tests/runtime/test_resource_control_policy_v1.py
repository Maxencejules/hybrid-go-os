"""M42 PR-2: deterministic resource-control policy checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_resource_control_campaign_v1 as resource_control  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def _check(data: dict, check_id: str) -> dict:
    rows = [entry for entry in data["checks"] if entry["check_id"] == check_id]
    assert len(rows) == 1
    return rows[0]


def test_resource_control_policy_v1_doc_declares_required_tokens():
    doc = _read("docs/runtime/resource_control_policy_v1.md")
    for token in [
        "Resource control policy ID: `rugo.resource_control_policy.v1`",
        "Parent namespace/cgroup contract ID: `rugo.namespace_cgroup_contract.v1`",
        "Resource control report schema: `rugo.resource_control_report.v1`",
        "Requirement schema: `rugo.resource_control_requirement_set.v1`",
        "`cpu_hard_quota_enforcement_ratio`",
        "`memory_hard_limit_enforcement_ratio`",
        "`io_bw_cap_enforcement_ratio`",
        "`pids_max_enforcement_ratio`",
        "`controller_drift_events`",
        "Local gate: `make test-isolation-baseline-v1`",
        "Local sub-gate: `make test-namespace-cgroup-v1`",
    ]:
        assert token in doc


def test_resource_control_campaign_v1_is_seed_deterministic():
    first = resource_control.run_campaign(seed=20260310)
    second = resource_control.run_campaign(seed=20260310)
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_resource_control_campaign_v1_schema_and_pass(tmp_path: Path):
    out = tmp_path / "resource-control-v1.json"
    rc = resource_control.main(["--seed", "20260310", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.resource_control_report.v1"
    assert data["policy_id"] == "rugo.resource_control_policy.v1"
    assert data["requirement_schema"] == "rugo.resource_control_requirement_set.v1"
    assert data["gate_pass"] is True
    assert data["summary"]["cpu"]["pass"] is True
    assert data["summary"]["memory"]["pass"] is True
    assert data["summary"]["io"]["pass"] is True
    assert data["summary"]["pids"]["pass"] is True
    assert data["summary"]["global"]["pass"] is True
    assert data["cpu"]["hard_quota_enforcement_ratio"] == 1.0
    assert data["memory"]["hard_limit_enforcement_ratio"] == 1.0
    assert data["io"]["bw_cap_enforcement_ratio"] == 1.0
    assert data["pids"]["max_enforcement_ratio"] == 1.0
    assert _check(data, "cpu_hard_quota_enforcement_ratio")["pass"] is True
    assert _check(data, "memory_hard_limit_enforcement_ratio")["pass"] is True
    assert _check(data, "controller_drift_events")["pass"] is True


def test_resource_control_campaign_v1_detects_drift_regression(tmp_path: Path):
    out = tmp_path / "resource-control-v1-fail.json"
    rc = resource_control.main(
        [
            "--inject-failure",
            "controller_drift_events",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["global"]["failures"] >= 1
    assert _check(data, "controller_drift_events")["pass"] is False


def test_resource_control_campaign_v1_rejects_unknown_check_id(tmp_path: Path):
    out = tmp_path / "resource-control-v1-error.json"
    rc = resource_control.main(
        [
            "--inject-failure",
            "resource_control_nonexistent_check",
            "--out",
            str(out),
        ]
    )
    assert rc == 2
    assert not out.exists()
