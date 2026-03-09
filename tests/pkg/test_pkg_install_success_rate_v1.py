"""M39 PR-2: deterministic package install success checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_pkg_install_success_campaign_v1 as campaign  # noqa: E402


def _check(data: dict, check_id: str) -> dict:
    rows = [entry for entry in data["checks"] if entry["check_id"] == check_id]
    assert len(rows) == 1
    return rows[0]


def test_pkg_install_success_campaign_v1_schema_and_pass(tmp_path: Path):
    out = tmp_path / "pkg-install-success-v1.json"
    rc = campaign.main(["--seed", "20260309", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.pkg_install_success_report.v1"
    assert data["ecosystem_policy_id"] == "rugo.ecosystem_scale_policy.v1"
    assert data["catalog_quality_contract_id"] == "rugo.catalog_quality_contract.v1"
    assert data["distribution_workflow_id"] == "rugo.distribution_workflow.v1"
    assert data["gate_pass"] is True
    assert data["total_failures"] == 0
    assert data["summary"]["install"]["pass"] is True
    assert data["summary"]["workflow"]["pass"] is True
    assert data["summary"]["recovery"]["pass"] is True
    assert data["summary"]["quality"]["pass"] is True
    assert data["install_success"]["stable_install_success_ratio"] >= 0.985
    assert data["install_success"]["canary_install_success_ratio"] >= 0.960
    assert data["install_success"]["edge_install_success_ratio"] >= 0.930
    assert data["latency"]["stable_install_p95_ms"] <= 75
    assert data["latency"]["canary_install_p95_ms"] <= 90
    assert data["latency"]["edge_install_p95_ms"] <= 110
    assert data["recovery"]["rollback_success_ratio"] >= 1.0
    assert data["quality"]["metadata_expiry_violations"] == 0
    assert data["quality"]["signature_verification_failures"] == 0
    assert _check(data, "stable_install_success_ratio")["pass"] is True
    assert _check(data, "rollback_success_ratio")["pass"] is True


def test_pkg_install_success_campaign_v1_detects_edge_regression(tmp_path: Path):
    out = tmp_path / "pkg-install-success-v1-fail.json"
    rc = campaign.main(
        [
            "--inject-failure",
            "edge_install_success_ratio",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["install"]["failures"] >= 1
    assert _check(data, "edge_install_success_ratio")["pass"] is False


def test_pkg_install_success_campaign_v1_rejects_unknown_check_id(tmp_path: Path):
    out = tmp_path / "pkg-install-success-v1-error.json"
    rc = campaign.main(
        [
            "--inject-failure",
            "install_nonexistent_check",
            "--out",
            str(out),
        ]
    )
    assert rc == 2
    assert not out.exists()
