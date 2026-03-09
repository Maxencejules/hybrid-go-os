"""M37 PR-1: hardware matrix v4 contract doc checks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_m37_pr1_hw_contract_artifacts_exist():
    required = [
        "docs/M37_EXECUTION_BACKLOG.md",
        "docs/hw/support_matrix_v4.md",
        "docs/hw/driver_lifecycle_contract_v4.md",
        "docs/hw/bare_metal_promotion_policy_v1.md",
        "tests/hw/test_hw_matrix_docs_v4.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M37 PR-1 artifact: {rel}"


def test_support_matrix_v4_doc_declares_required_tokens():
    doc = _read("docs/hw/support_matrix_v4.md")
    for token in [
        "Milestone: M37 Hardware Breadth + Driver Matrix v4",
        "Tier 0",
        "Tier 1",
        "Tier 2",
        "Tier 3",
        "Tier 4",
        "Schema identifier: `rugo.hw_matrix_evidence.v4`",
        "Local gate: `make test-hw-matrix-v4`.",
        "Local sub-gate: `make test-hw-baremetal-promotion-v1`.",
        "CI gate: `Hardware matrix v4 gate`.",
        "CI sub-gate: `Hardware bare-metal promotion v1 gate`.",
        "Hardware support claims are bounded to matrix v4 evidence only.",
    ]:
        assert token in doc


def test_driver_lifecycle_contract_v4_doc_declares_required_tokens():
    doc = _read("docs/hw/driver_lifecycle_contract_v4.md")
    for token in [
        "Schema identifier: `rugo.driver_lifecycle_report.v4`",
        "`probe_missing`",
        "`probe_found`",
        "`init_ready`",
        "`runtime_ok`",
        "`reset_recover`",
        "`error_recoverable`",
        "`error_fatal`",
        "`BLK: not found`",
        "`NET: not found`",
        "`virtio-blk-pci`, `ahci`, `nvme`",
        "`virtio-net-pci`, `e1000`, `rtl8139`",
    ]:
        assert token in doc


def test_bare_metal_promotion_policy_v1_doc_declares_required_tokens():
    doc = _read("docs/hw/bare_metal_promotion_policy_v1.md")
    for token in [
        "Policy identifier: `rugo.hw_baremetal_promotion_policy.v1`.",
        "Report schema: `rugo.hw_baremetal_promotion_report.v1`.",
        "Matrix evidence schema: `rugo.hw_matrix_evidence.v4`.",
        "Minimum consecutive green runs: `12`.",
        "Minimum campaign pass rate: `0.98`.",
        "`out/pytest-hw-matrix-v4.xml`",
        "`out/hw-matrix-v4.json`",
        "`out/hw-promotion-v1.json`",
        "Local gate: `make test-hw-matrix-v4`.",
        "Local sub-gate: `make test-hw-baremetal-promotion-v1`.",
        "CI gate: `Hardware matrix v4 gate`.",
        "CI sub-gate: `Hardware bare-metal promotion v1 gate`.",
    ]:
        assert token in doc


def test_m35_m39_roadmap_anchor_declares_m37_gates():
    roadmap = _read("docs/M35_M39_GENERAL_PURPOSE_EXPANSION_ROADMAP.md")
    assert "test-hw-matrix-v4" in roadmap
    assert "test-hw-baremetal-promotion-v1" in roadmap
