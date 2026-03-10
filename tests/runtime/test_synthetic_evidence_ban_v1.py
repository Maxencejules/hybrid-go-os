"""M40 aggregate sub-gate: synthetic evidence ban v1 wiring and enforcement."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import audit_gate_evidence_v1 as audit  # noqa: E402
import collect_runtime_evidence_v1 as collector  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _check(data: dict, check_id: str) -> dict:
    rows = [entry for entry in data["checks"] if entry["check_id"] == check_id]
    assert len(rows) == 1
    return rows[0]


def test_synthetic_evidence_ban_v1_wiring_and_artifacts(tmp_path: Path):
    required = [
        "docs/M40_EXECUTION_BACKLOG.md",
        "docs/runtime/evidence_integrity_policy_v1.md",
        "docs/runtime/gate_provenance_policy_v1.md",
        "tools/collect_runtime_evidence_v1.py",
        "tools/audit_gate_evidence_v1.py",
        "tests/runtime/test_gate_evidence_audit_v1.py",
        "tests/runtime/test_synthetic_evidence_ban_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M40 synthetic-ban artifact: {rel}"

    roadmap = _read("docs/M40_M44_GENERAL_PURPOSE_PARITY_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M40_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-synthetic-evidence-ban-v1" in roadmap

    assert "test-synthetic-evidence-ban-v1" in makefile
    for entry in [
        "tools/collect_runtime_evidence_v1.py --out $(OUT)/runtime-evidence-v1.json",
        "tools/audit_gate_evidence_v1.py --evidence $(OUT)/runtime-evidence-v1.json --out $(OUT)/gate-evidence-audit-v1.json",
        "tests/runtime/test_evidence_integrity_docs_v1.py",
        "tests/runtime/test_gate_evidence_audit_v1.py",
        "tests/runtime/test_synthetic_evidence_ban_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-synthetic-evidence-ban-v1.xml" in makefile

    assert "Synthetic evidence ban v1 gate" in ci
    assert "make test-synthetic-evidence-ban-v1" in ci
    assert "synthetic-evidence-ban-v1-artifacts" in ci
    assert "out/pytest-synthetic-evidence-ban-v1.xml" in ci
    assert "out/runtime-evidence-v1.json" in ci
    assert "out/gate-evidence-audit-v1.json" in ci

    assert "Status: done" in backlog
    assert "M40" in milestones
    assert "M40" in status
    assert "M40 execution backlog (completed)" in readme

    runtime_out = tmp_path / "runtime-evidence-v1.json"
    audit_out = tmp_path / "gate-evidence-audit-v1.json"
    synthetic_runtime_out = tmp_path / "runtime-evidence-v1-synthetic.json"
    synthetic_audit_out = tmp_path / "gate-evidence-audit-v1-synthetic.json"

    assert collector.main(["--seed", "20260310", "--out", str(runtime_out)]) == 0
    assert audit.main(["--evidence", str(runtime_out), "--out", str(audit_out)]) == 0

    baseline_audit = json.loads(audit_out.read_text(encoding="utf-8"))
    assert baseline_audit["gate_pass"] is True
    assert baseline_audit["total_failures"] == 0
    assert _check(baseline_audit, "synthetic_only_artifacts")["pass"] is True

    assert (
        collector.main(
            [
                "--inject-failure",
                "synthetic_only_artifacts",
                "--out",
                str(synthetic_runtime_out),
            ]
        )
        == 1
    )
    assert (
        audit.main(
            ["--evidence", str(synthetic_runtime_out), "--out", str(synthetic_audit_out)]
        )
        == 1
    )

    synthetic_audit = json.loads(synthetic_audit_out.read_text(encoding="utf-8"))
    assert synthetic_audit["gate_pass"] is False
    assert _check(synthetic_audit, "synthetic_only_artifacts")["pass"] is False
