"""M39 PR-2: deterministic distribution workflow checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_pkg_install_success_campaign_v1 as install  # noqa: E402
import run_reproducible_catalog_audit_v1 as audit  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_distribution_workflow_v1_doc_declares_required_tokens():
    doc = _read("docs/pkg/distribution_workflow_v1.md")
    for token in [
        "Policy ID: `rugo.distribution_workflow.v1`.",
        "Workflow report schema: `rugo.catalog_reproducibility_audit_report.v1`.",
        "`ingest`",
        "`vet`",
        "`sign`",
        "`stage`",
        "`rollout`",
        "`rollback`",
        "Workflow stage completeness ratio: `>= 1.0`.",
        "Release signoff ratio: `>= 1.0`.",
        "Rollback drill pass ratio: `>= 1.0`.",
        "Mirror index consistency ratio: `>= 1.0`.",
        "Replication lag p95 minutes: `<= 15`.",
    ]:
        assert token in doc


def test_distribution_workflow_v1_artifacts_pass(tmp_path: Path):
    install_out = tmp_path / "pkg-install-success-v1.json"
    audit_out = tmp_path / "catalog-audit-v1.json"

    assert install.main(["--seed", "20260309", "--out", str(install_out)]) == 0
    assert audit.main(["--seed", "20260309", "--out", str(audit_out)]) == 0

    install_data = json.loads(install_out.read_text(encoding="utf-8"))
    audit_data = json.loads(audit_out.read_text(encoding="utf-8"))

    assert install_data["distribution_workflow_id"] == "rugo.distribution_workflow.v1"
    assert install_data["gate_pass"] is True
    assert install_data["total_failures"] == 0

    assert audit_data["distribution_workflow_id"] == "rugo.distribution_workflow.v1"
    assert audit_data["gate_pass"] is True
    assert audit_data["total_failures"] == 0
    assert audit_data["summary"]["workflow"]["pass"] is True


def test_distribution_workflow_v1_detects_workflow_stage_failure(tmp_path: Path):
    out = tmp_path / "catalog-audit-v1-workflow-fail.json"
    rc = audit.main(
        [
            "--inject-failure",
            "workflow_stage_completeness_ratio",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["workflow"]["failures"] >= 1
