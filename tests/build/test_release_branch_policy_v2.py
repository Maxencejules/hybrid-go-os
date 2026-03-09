"""M31 PR-2: release branch policy v2 audit checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import release_branch_audit_v2 as audit_tool  # noqa: E402


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def test_release_branch_audit_v2_deterministic():
    first = audit_tool.run_audit(
        branches=["release/1.0", "release/1.1", "hotfix/1.1.1"],
        required_branches=["release/1.0", "release/1.1"],
        allow_hotfix=True,
    )
    second = audit_tool.run_audit(
        branches=["release/1.0", "release/1.1", "hotfix/1.1.1"],
        required_branches=["release/1.0", "release/1.1"],
        allow_hotfix=True,
    )
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_release_branch_audit_v2_schema_and_gate_pass(tmp_path: Path):
    out = tmp_path / "release-branch-audit-v2.json"
    rc = audit_tool.main(
        [
            "--branch",
            "release/1.0",
            "--branch",
            "release/1.1",
            "--branch",
            "hotfix/1.1.1",
            "--required-branch",
            "release/1.0",
            "--required-branch",
            "release/1.1",
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.release_branch_audit.v2"
    assert data["policy_id"] == "rugo.release_policy.v2"
    assert data["total_failures"] == 0
    assert data["meets_target"] is True
    assert data["missing_required_branches"] == []
    checks = {check["name"]: check["pass"] for check in data["checks"]}
    assert checks["branch_naming_compliant"] is True
    assert checks["required_branches_present"] is True


def test_release_branch_audit_v2_detects_missing_required_branch(tmp_path: Path):
    out = tmp_path / "release-branch-audit-v2.json"
    rc = audit_tool.main(
        [
            "--branch",
            "release/1.0",
            "--required-branch",
            "release/1.0",
            "--required-branch",
            "release/1.1",
            "--out",
            str(out),
        ]
    )
    assert rc == 1
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.release_branch_audit.v2"
    assert "release/1.1" in data["missing_required_branches"]
    assert data["meets_target"] is False
