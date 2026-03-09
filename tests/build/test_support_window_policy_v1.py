"""M31 PR-2: support lifecycle policy v1 audit checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import support_window_audit_v1 as audit_tool  # noqa: E402


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def test_support_window_audit_v1_deterministic():
    first = audit_tool.run_audit(
        window_specs=[
            "stable:180:45:7:90",
            "lts:730:140:14:365",
        ],
        required_channels=["stable", "lts"],
        max_security_sla_days=14,
        min_backport_window_days=21,
    )
    second = audit_tool.run_audit(
        window_specs=[
            "stable:180:45:7:90",
            "lts:730:140:14:365",
        ],
        required_channels=["stable", "lts"],
        max_security_sla_days=14,
        min_backport_window_days=21,
    )
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_support_window_audit_v1_schema_and_gate_pass(tmp_path: Path):
    out = tmp_path / "support-window-audit-v1.json"
    rc = audit_tool.main(
        [
            "--window",
            "stable:180:45:7:90",
            "--window",
            "lts:730:140:14:365",
            "--required-channel",
            "stable",
            "--required-channel",
            "lts",
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.support_window_audit.v1"
    assert data["policy_id"] == "rugo.support_lifecycle_policy.v1"
    assert data["total_failures"] == 0
    assert data["meets_target"] is True
    checks = {check["name"]: check["pass"] for check in data["checks"]}
    assert checks["required_channels_present"] is True
    assert checks["all_channels_within_support_window"] is True
    assert checks["security_sla_within_threshold"] is True


def test_support_window_audit_v1_detects_expired_window(tmp_path: Path):
    out = tmp_path / "support-window-audit-v1.json"
    rc = audit_tool.main(
        [
            "--window",
            "stable:180:190:7:90",
            "--window",
            "lts:730:140:14:365",
            "--required-channel",
            "stable",
            "--required-channel",
            "lts",
            "--out",
            str(out),
        ]
    )
    assert rc == 1
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.support_window_audit.v1"
    assert data["meets_target"] is False
    checks = {check["name"]: check["pass"] for check in data["checks"]}
    assert checks["all_channels_within_support_window"] is False
