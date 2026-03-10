"""M45 PR-1: hardware matrix v6 and display bridge contract doc checks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_m45_pr1_hw_contract_artifacts_exist():
    required = [
        "docs/M45_EXECUTION_BACKLOG.md",
        "docs/hw/support_matrix_v6.md",
        "docs/hw/driver_lifecycle_contract_v6.md",
        "docs/hw/virtio_platform_profile_v1.md",
        "docs/desktop/display_stack_contract_v1.md",
        "tests/hw/test_hw_matrix_docs_v6.py",
        "tests/hw/test_virtio_platform_profile_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M45 PR-1 artifact: {rel}"


def test_support_matrix_v6_doc_declares_required_tokens():
    doc = _read("docs/hw/support_matrix_v6.md")
    for token in [
        "Milestone: M45 Modern Virtual Platform Parity v1",
        "Tier 0",
        "Tier 1",
        "Tier 2",
        "Tier 3",
        "Tier 4",
        "Schema identifier: `rugo.hw_matrix_evidence.v6`",
        "Driver contract ID: `rugo.driver_lifecycle_report.v6`",
        "VirtIO platform profile ID: `rugo.virtio_platform_profile.v1`",
        "Display contract ID: `rugo.display_stack_contract.v1`",
        "Shadow baseline contract ID: `rugo.hw.support_matrix.v5`",
        "Local gate: `make test-hw-matrix-v6`.",
        "Local sub-gate: `make test-virtio-platform-v1`.",
        "CI gate: `Hardware matrix v6 shadow gate`.",
        "CI sub-gate: `Virtio platform v1 shadow gate`.",
        "minimum `14` consecutive green shadow runs",
    ]:
        assert token in doc


def test_driver_lifecycle_contract_v6_doc_declares_required_tokens():
    doc = _read("docs/hw/driver_lifecycle_contract_v6.md")
    for token in [
        "Schema identifier: `rugo.driver_lifecycle_report.v6`",
        "`probe_missing`",
        "`probe_found`",
        "`init_ready`",
        "`runtime_ok`",
        "`irq_vector_bound`",
        "`irq_vector_retarget`",
        "`cpu_affinity_balance`",
        "`reset_recover`",
        "`framebuffer_console_present`",
        "`display_scanout_ready`",
        "`error_recoverable`",
        "`error_fatal`",
        "`BLK: not found`",
        "`NET: not found`",
        "`SCSI: not found`",
        "`GPU: not found`",
        "`virtio-blk-pci` transitional",
        "`virtio-net-pci` modern",
        "`virtio-scsi-pci`",
        "`virtio-gpu-pci`",
    ]:
        assert token in doc


def test_virtio_platform_profile_v1_doc_declares_required_tokens():
    doc = _read("docs/hw/virtio_platform_profile_v1.md")
    for token in [
        "VirtIO platform profile ID: `rugo.virtio_platform_profile.v1`",
        "Parent matrix contract: `rugo.hw.support_matrix.v6`",
        "Driver lifecycle contract: `rugo.driver_lifecycle_report.v6`",
        "Display contract: `rugo.display_stack_contract.v1`",
        "`transitional`",
        "`modern`",
        "`virtio-blk-pci,disable-modern=on`",
        "`virtio-net-pci,disable-modern=on`",
        "`virtio-scsi-pci`",
        "`virtio-gpu-pci`",
        "`boot_transport_class`",
        "`display_class`",
        "`desktop_display_checks`",
        "Local shadow sub-gate: `make test-virtio-platform-v1`",
        "CI shadow sub-gate: `Virtio platform v1 shadow gate`",
    ]:
        assert token in doc


def test_display_contract_v1_doc_declares_bridge_tokens():
    doc = _read("docs/desktop/display_stack_contract_v1.md")
    for token in [
        "Display device bridge requirements",
        "`display_class`",
        "`display_device`",
        "`boot_transport_class`",
        "`desktop_display_checks`",
        "`virtio-gpu-pci`",
    ]:
        assert token in doc


def test_m45_roadmap_anchor_declares_shadow_gates():
    roadmap = _read("docs/M45_M47_HARDWARE_EXPANSION_ROADMAP.md")
    assert "test-hw-matrix-v6" in roadmap
    assert "test-virtio-platform-v1" in roadmap
