"""M40 PR-2: deterministic gate evidence provenance audit checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import audit_gate_evidence_v1 as audit  # noqa: E402
import collect_runtime_evidence_v1 as collector  # noqa: E402


def _check(data: dict, check_id: str) -> dict:
    rows = [entry for entry in data["checks"] if entry["check_id"] == check_id]
    assert len(rows) == 1
    return rows[0]


def test_gate_evidence_audit_v1_schema_and_pass(tmp_path: Path):
    evidence_out = tmp_path / "runtime-evidence-v1.json"
    audit_out = tmp_path / "gate-evidence-audit-v1.json"

    assert collector.main(["--seed", "20260310", "--out", str(evidence_out)]) == 0
    assert audit.main(["--evidence", str(evidence_out), "--out", str(audit_out)]) == 0

    data = json.loads(audit_out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.gate_evidence_audit_report.v1"
    assert data["audit_policy_id"] == "rugo.gate_provenance_policy.v1"
    assert data["evidence_integrity_policy_id"] == "rugo.evidence_integrity_policy.v1"
    assert data["runtime_evidence_schema_id"] == "rugo.runtime_evidence_schema.v1"
    assert data["required_evidence_schema"] == "rugo.runtime_evidence_report.v1"
    assert data["gate"] == "test-synthetic-evidence-ban-v1"
    assert data["gate_pass"] is True
    assert data["total_failures"] == 0
    assert _check(data, "runtime_capture_ratio")["pass"] is True
    assert _check(data, "trace_linkage_ratio")["pass"] is True
    assert _check(data, "synthetic_only_artifacts")["pass"] is True


def test_gate_evidence_audit_detects_synthetic_only_artifacts(tmp_path: Path):
    evidence_out = tmp_path / "runtime-evidence-v1-synthetic.json"
    audit_out = tmp_path / "gate-evidence-audit-v1-synthetic.json"

    assert (
        collector.main(
            [
                "--inject-failure",
                "synthetic_only_artifacts",
                "--out",
                str(evidence_out),
            ]
        )
        == 1
    )
    assert audit.main(["--evidence", str(evidence_out), "--out", str(audit_out)]) == 1

    data = json.loads(audit_out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["synthetic"]["failures"] >= 1
    assert _check(data, "synthetic_only_artifacts")["pass"] is False


def test_gate_evidence_audit_rejects_unknown_check_id(tmp_path: Path):
    out = tmp_path / "gate-evidence-audit-v1-error.json"
    rc = audit.main(
        [
            "--inject-failure",
            "audit_nonexistent_check",
            "--out",
            str(out),
        ]
    )
    assert rc == 2
    assert not out.exists()
