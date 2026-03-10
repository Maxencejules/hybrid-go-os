"""M40 PR-2: deterministic runtime evidence collection checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import collect_runtime_evidence_v1 as collector  # noqa: E402


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def _check(data: dict, check_id: str) -> dict:
    rows = [entry for entry in data["checks"] if entry["check_id"] == check_id]
    assert len(rows) == 1
    return rows[0]


def test_runtime_evidence_report_is_seed_deterministic():
    first = collector.collect_runtime_evidence(seed=20260310)
    second = collector.collect_runtime_evidence(seed=20260310)
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_runtime_evidence_collection_v1_schema_and_pass(tmp_path: Path):
    out = tmp_path / "runtime-evidence-v1.json"
    rc = collector.main(["--seed", "20260310", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.runtime_evidence_report.v1"
    assert data["evidence_integrity_policy_id"] == "rugo.evidence_integrity_policy.v1"
    assert data["runtime_evidence_schema_id"] == "rugo.runtime_evidence_schema.v1"
    assert data["gate_provenance_policy_id"] == "rugo.gate_provenance_policy.v1"
    assert data["gate"] == "test-evidence-integrity-v1"
    assert data["gate_pass"] is True
    assert data["total_failures"] == 0
    assert data["summary"]["execution"]["pass"] is True
    assert data["summary"]["provenance"]["pass"] is True
    assert data["summary"]["synthetic"]["pass"] is True
    assert data["totals"]["evidence_items"] >= 4
    assert data["totals"]["synthetic_items"] == 0

    lanes = {trace["execution_lane"] for trace in data["traces"]}
    assert {"qemu", "baremetal"}.issubset(lanes)

    for item in data["evidence_items"]:
        assert item["synthetic"] is False
        assert item["trace_id"]
        assert item["trace_digest"]
        assert item["signature"]["valid"] is True

    assert _check(data, "trace_linkage_ratio")["pass"] is True
    assert _check(data, "synthetic_only_artifacts")["pass"] is True


def test_runtime_evidence_collection_detects_synthetic_only_failure(tmp_path: Path):
    out = tmp_path / "runtime-evidence-v1-fail.json"
    rc = collector.main(
        [
            "--inject-failure",
            "synthetic_only_artifacts",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["synthetic"]["failures"] >= 1
    assert _check(data, "synthetic_only_artifacts")["pass"] is False


def test_runtime_evidence_collection_rejects_unknown_check_id(tmp_path: Path):
    out = tmp_path / "runtime-evidence-v1-error.json"
    rc = collector.main(
        [
            "--inject-failure",
            "runtime_nonexistent_check",
            "--out",
            str(out),
        ]
    )
    assert rc == 2
    assert not out.exists()
