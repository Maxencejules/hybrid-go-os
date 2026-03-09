"""M39 PR-1: ecosystem scale and distribution workflow doc checks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_m39_pr1_ecosystem_contract_artifacts_exist():
    required = [
        "docs/M39_EXECUTION_BACKLOG.md",
        "docs/pkg/ecosystem_scale_policy_v1.md",
        "docs/pkg/catalog_quality_contract_v1.md",
        "docs/pkg/distribution_workflow_v1.md",
        "tests/pkg/test_ecosystem_scale_docs_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M39 PR-1 artifact: {rel}"


def test_ecosystem_scale_policy_v1_doc_declares_required_tokens():
    doc = _read("docs/pkg/ecosystem_scale_policy_v1.md")
    for token in [
        "Policy ID: `rugo.ecosystem_scale_policy.v1`.",
        "Catalog quality contract ID: `rugo.catalog_quality_contract.v1`.",
        "Distribution workflow ID: `rugo.distribution_workflow.v1`.",
        "App catalog simulation schema: `rugo.app_catalog_sim_report.v1`.",
        "Install success campaign schema: `rugo.pkg_install_success_report.v1`.",
        "Reproducibility audit schema: `rugo.catalog_reproducibility_audit_report.v1`.",
        "Total catalog entries: `>= 420`.",
        "Class coverage floor per declared class: `>= 70`.",
        "Catalog metadata completeness ratio: `>= 0.995`.",
        "Signed provenance coverage ratio: `>= 1.0`.",
        "Unsupported workload ratio: `<= 0.02`.",
        "Local gate: `make test-ecosystem-scale-v1`.",
        "Local sub-gate: `make test-app-catalog-health-v1`.",
        "CI gate: `Ecosystem scale v1 gate`.",
        "CI sub-gate: `App catalog health v1 gate`.",
    ]:
        assert token in doc


def test_catalog_quality_contract_v1_doc_declares_required_tokens():
    doc = _read("docs/pkg/catalog_quality_contract_v1.md")
    for token in [
        "Contract ID: `rugo.catalog_quality_contract.v1`.",
        "Parent ecosystem policy ID: `rugo.ecosystem_scale_policy.v1`.",
        "Install success campaign schema: `rugo.pkg_install_success_report.v1`.",
        "Reproducibility audit schema: `rugo.catalog_reproducibility_audit_report.v1`.",
        "Stable install success ratio: `>= 0.985`.",
        "Canary install success ratio: `>= 0.960`.",
        "Edge install success ratio: `>= 0.930`.",
        "Stable install latency p95: `<= 75 ms`.",
        "Rollback success ratio: `>= 1.0`.",
        "Metadata expiry violations: `0`.",
        "Signature verification failures: `0`.",
    ]:
        assert token in doc


def test_distribution_workflow_v1_doc_declares_required_tokens():
    doc = _read("docs/pkg/distribution_workflow_v1.md")
    for token in [
        "Policy ID: `rugo.distribution_workflow.v1`.",
        "Parent ecosystem policy ID: `rugo.ecosystem_scale_policy.v1`.",
        "Parent catalog quality contract ID: `rugo.catalog_quality_contract.v1`.",
        "Workflow report schema: `rugo.catalog_reproducibility_audit_report.v1`.",
        "Workflow stage completeness ratio: `>= 1.0`.",
        "Release signoff ratio: `>= 1.0`.",
        "Rollback drill pass ratio: `>= 1.0`.",
        "Mirror index consistency ratio: `>= 1.0`.",
        "Replication lag p95 minutes: `<= 15`.",
        "Unresolved policy exceptions: `0`.",
        "Local gate: `make test-ecosystem-scale-v1`.",
        "Local sub-gate: `make test-app-catalog-health-v1`.",
    ]:
        assert token in doc


def test_m35_m39_roadmap_anchor_declares_m39_gates():
    roadmap = _read("docs/M35_M39_GENERAL_PURPOSE_EXPANSION_ROADMAP.md")
    assert "test-ecosystem-scale-v1" in roadmap
    assert "test-app-catalog-health-v1" in roadmap
