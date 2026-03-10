"""M43 PR-1: hardware matrix v5 + firmware/SMP contract doc checks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_m43_pr1_hw_contract_artifacts_exist():
    required = [
        "docs/M43_EXECUTION_BACKLOG.md",
        "docs/hw/support_matrix_v5.md",
        "docs/hw/driver_lifecycle_contract_v5.md",
        "docs/hw/acpi_uefi_hardening_v3.md",
        "docs/runtime/smp_interrupt_model_v1.md",
        "tests/hw/test_hw_matrix_docs_v5.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M43 PR-1 artifact: {rel}"


def test_support_matrix_v5_doc_declares_required_tokens():
    doc = _read("docs/hw/support_matrix_v5.md")
    for token in [
        "Milestone: M43 Hardware/Firmware Breadth + SMP v1",
        "Tier 0",
        "Tier 1",
        "Tier 2",
        "Tier 3",
        "Tier 4",
        "Schema identifier: `rugo.hw_matrix_evidence.v5`",
        "Firmware contract ID: `rugo.acpi_uefi_hardening.v3`",
        "SMP contract ID: `rugo.smp_interrupt_model.v1`",
        "Local gate: `make test-hw-firmware-smp-v1`.",
        "Local sub-gate: `make test-native-driver-matrix-v1`.",
        "CI gate: `Hardware firmware smp v1 gate`.",
        "CI sub-gate: `Native driver matrix v1 gate`.",
        "Hardware support claims are bounded to matrix v5 evidence only.",
    ]:
        assert token in doc


def test_driver_lifecycle_contract_v5_doc_declares_required_tokens():
    doc = _read("docs/hw/driver_lifecycle_contract_v5.md")
    for token in [
        "Schema identifier: `rugo.driver_lifecycle_report.v5`",
        "`probe_missing`",
        "`probe_found`",
        "`init_ready`",
        "`runtime_ok`",
        "`irq_vector_bound`",
        "`irq_vector_retarget`",
        "`cpu_affinity_balance`",
        "`reset_recover`",
        "`error_recoverable`",
        "`error_fatal`",
        "`BLK: not found`",
        "`NET: not found`",
        "`IRQ: vector bound`",
        "`SMP: affinity balanced`",
        "`virtio-blk-pci`, `ahci`, `nvme`",
        "`virtio-net-pci`, `e1000`, `rtl8139`",
    ]:
        assert token in doc


def test_acpi_uefi_hardening_v3_doc_declares_required_tokens():
    doc = _read("docs/hw/acpi_uefi_hardening_v3.md")
    for token in [
        "Hardening identifier: `rugo.acpi_uefi_hardening.v3`.",
        "Parent matrix schema: `rugo.hw_matrix_evidence.v5`.",
        "SMP model ID: `rugo.smp_interrupt_model.v1`.",
        "`RSDP`",
        "`XSDT`",
        "`MADT`",
        "checksum",
        "safe fallback path",
        "deterministic",
    ]:
        assert token in doc


def test_smp_interrupt_model_v1_doc_declares_required_tokens():
    doc = _read("docs/runtime/smp_interrupt_model_v1.md")
    for token in [
        "SMP interrupt model ID: `rugo.smp_interrupt_model.v1`.",
        "Matrix evidence schema: `rugo.hw_matrix_evidence.v5`.",
        "Firmware evidence schema: `rugo.hw_firmware_smp_evidence.v1`.",
        "`bootstrap_cpu_online_ratio`",
        "`application_cpu_online_ratio`",
        "`ipi_roundtrip_p95_ms`",
        "`irq_affinity_drift`",
        "`lost_interrupt_events`",
        "Local gate: `make test-hw-firmware-smp-v1`.",
        "Local sub-gate: `make test-native-driver-matrix-v1`.",
    ]:
        assert token in doc


def test_m40_m44_roadmap_anchor_declares_m43_gates():
    roadmap = _read("docs/M40_M44_GENERAL_PURPOSE_PARITY_ROADMAP.md")
    assert "test-hw-firmware-smp-v1" in roadmap
    assert "test-native-driver-matrix-v1" in roadmap
