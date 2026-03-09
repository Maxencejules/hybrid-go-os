"""M39 aggregate sub-gate: app catalog health v1 wiring and artifacts."""

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


def test_app_catalog_health_gate_v1_wiring_and_artifacts(tmp_path: Path):
    required = [
        "docs/M39_EXECUTION_BACKLOG.md",
        "docs/pkg/catalog_quality_contract_v1.md",
        "docs/pkg/distribution_workflow_v1.md",
        "tools/run_pkg_install_success_campaign_v1.py",
        "tools/run_reproducible_catalog_audit_v1.py",
        "tests/pkg/test_ecosystem_scale_docs_v1.py",
        "tests/pkg/test_pkg_install_success_rate_v1.py",
        "tests/pkg/test_catalog_reproducibility_v1.py",
        "tests/pkg/test_distribution_workflow_v1.py",
        "tests/pkg/test_app_catalog_health_gate_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M39 app-catalog-health artifact: {rel}"

    roadmap = _read("docs/M35_M39_GENERAL_PURPOSE_EXPANSION_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M39_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-app-catalog-health-v1" in roadmap

    assert "test-app-catalog-health-v1" in makefile
    for entry in [
        "tools/run_pkg_install_success_campaign_v1.py --out $(OUT)/pkg-install-success-v1.json",
        "tools/run_reproducible_catalog_audit_v1.py --out $(OUT)/catalog-audit-v1.json",
        "tests/pkg/test_ecosystem_scale_docs_v1.py",
        "tests/pkg/test_pkg_install_success_rate_v1.py",
        "tests/pkg/test_catalog_reproducibility_v1.py",
        "tests/pkg/test_distribution_workflow_v1.py",
        "tests/pkg/test_app_catalog_health_gate_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-app-catalog-health-v1.xml" in makefile

    assert "App catalog health v1 gate" in ci
    assert "make test-app-catalog-health-v1" in ci
    assert "app-catalog-health-v1-artifacts" in ci
    assert "out/pytest-app-catalog-health-v1.xml" in ci
    assert "out/pkg-install-success-v1.json" in ci
    assert "out/catalog-audit-v1.json" in ci

    assert "Status: done" in backlog
    assert "M39" in milestones
    assert "M39" in status
    assert "M39" in readme

    install_out = tmp_path / "pkg-install-success-v1.json"
    audit_out = tmp_path / "catalog-audit-v1.json"

    assert install.main(["--seed", "20260309", "--out", str(install_out)]) == 0
    assert audit.main(["--seed", "20260309", "--out", str(audit_out)]) == 0

    install_data = json.loads(install_out.read_text(encoding="utf-8"))
    audit_data = json.loads(audit_out.read_text(encoding="utf-8"))

    assert install_data["schema"] == "rugo.pkg_install_success_report.v1"
    assert install_data["catalog_quality_contract_id"] == "rugo.catalog_quality_contract.v1"
    assert install_data["gate_pass"] is True
    assert install_data["total_failures"] == 0

    assert audit_data["schema"] == "rugo.catalog_reproducibility_audit_report.v1"
    assert audit_data["distribution_workflow_id"] == "rugo.distribution_workflow.v1"
    assert audit_data["gate_pass"] is True
    assert audit_data["total_failures"] == 0
