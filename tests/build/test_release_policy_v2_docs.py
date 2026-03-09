"""M31 PR-1: release lifecycle and support policy doc contract checks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_m31_pr1_release_policy_artifacts_exist():
    required = [
        "docs/M31_EXECUTION_BACKLOG.md",
        "docs/build/release_policy_v2.md",
        "docs/build/support_lifecycle_policy_v1.md",
        "tests/build/test_release_policy_v2_docs.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M31 PR-1 artifact: {rel}"


def test_release_policy_v2_doc_declares_required_tokens():
    doc = _read("docs/build/release_policy_v2.md")
    for token in [
        "Release lifecycle policy ID: `rugo.release_policy.v2`",
        "Branch audit schema: `rugo.release_branch_audit.v2`",
        "Support window audit schema: `rugo.support_window_audit.v1`",
        "support window: 180 days",
        "support window: 730 days",
        "Security fix SLA must be less than or equal to 14 days.",
        "Local gate: `make test-release-lifecycle-v2`",
        "CI gate: `Release lifecycle v2 gate`",
        "CI sub-gate: `Supply-chain revalidation v1 gate`",
    ]:
        assert token in doc


def test_support_lifecycle_policy_v1_doc_declares_required_tokens():
    doc = _read("docs/build/support_lifecycle_policy_v1.md")
    for token in [
        "Support lifecycle policy ID: `rugo.support_lifecycle_policy.v1`",
        "Audit schema: `rugo.support_window_audit.v1`",
        "`stable`",
        "`lts`",
        "minimum support window: 180 days",
        "minimum support window: 730 days",
        "maximum security fix SLA: 14 days",
        "minimum backport window: 21 days",
        "minimum backport window: 180 days",
        "Lifecycle gate: `make test-release-lifecycle-v2`",
    ]:
        assert token in doc


def test_m31_roadmap_anchor_declares_release_lifecycle_gate():
    roadmap = _read("docs/M21_M34_MATURITY_PARITY_ROADMAP.md")
    assert "test-release-lifecycle-v2" in roadmap
    assert "test-supply-chain-revalidation-v1" in roadmap
