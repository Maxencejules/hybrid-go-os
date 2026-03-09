"""M37 PR-2: deterministic bare-metal promotion policy checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import collect_hw_promotion_evidence_v1 as promotion  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def test_baremetal_promotion_policy_v1_doc_declares_required_tokens():
    policy = _read("docs/hw/bare_metal_promotion_policy_v1.md")
    for token in [
        "Policy identifier: `rugo.hw_baremetal_promotion_policy.v1`.",
        "Report schema: `rugo.hw_baremetal_promotion_report.v1`.",
        "Matrix evidence schema: `rugo.hw_matrix_evidence.v4`.",
        "Minimum consecutive green runs: `12`.",
        "Minimum campaign pass rate: `0.98`.",
        "`out/pytest-hw-matrix-v4.xml`",
        "`out/hw-matrix-v4.json`",
        "`out/hw-promotion-v1.json`",
    ]:
        assert token in policy


def test_baremetal_promotion_report_v1_is_seed_deterministic():
    first = promotion.run_promotion(
        seed=20260309,
        campaign_runs=12,
        required_consecutive_green=12,
        min_pass_rate=0.98,
    )
    second = promotion.run_promotion(
        seed=20260309,
        campaign_runs=12,
        required_consecutive_green=12,
        min_pass_rate=0.98,
    )
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_baremetal_promotion_report_v1_schema_and_gate_pass(tmp_path: Path):
    out = tmp_path / "hw-promotion-v1.json"
    rc = promotion.main(["--seed", "20260309", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.hw_baremetal_promotion_report.v1"
    assert data["policy_id"] == "rugo.hw_baremetal_promotion_policy.v1"
    assert data["matrix_schema_id"] == "rugo.hw_matrix_evidence.v4"
    assert data["gate_pass"] is True
    assert data["total_failures"] == 0
    assert data["summary"]["pass_rate"] >= 0.98
    assert data["summary"]["trailing_consecutive_green"] >= 12
    assert data["missing_artifacts"] == []


def test_baremetal_promotion_report_v1_detects_missing_artifact(tmp_path: Path):
    out = tmp_path / "hw-promotion-v1-missing-artifact.json"
    rc = promotion.main(
        [
            "--inject-missing-artifact",
            "matrix_junit",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert "matrix_junit" in data["missing_artifacts"]
    assert "artifact_bundle_complete" in data["failures"]


def test_baremetal_promotion_report_v1_rejects_unknown_artifact(tmp_path: Path):
    out = tmp_path / "hw-promotion-v1-error.json"
    rc = promotion.main(
        [
            "--inject-missing-artifact",
            "unknown_artifact",
            "--out",
            str(out),
        ]
    )
    assert rc == 2
    assert not out.exists()
