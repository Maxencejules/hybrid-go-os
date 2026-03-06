"""M15 aggregate gate: hardware matrix v2 contract and gate wiring."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_hw_matrix_v2_gate_wiring_and_artifacts():
    required = [
        "docs/M15_EXECUTION_BACKLOG.md",
        "docs/hw/support_matrix_v2.md",
        "docs/hw/device_profile_contract_v2.md",
        "docs/hw/dma_iommu_strategy_v2.md",
        "docs/hw/acpi_uefi_hardening_v2.md",
        "docs/hw/bare_metal_bringup_v2.md",
        "tests/hw/test_hardware_matrix_v2.py",
        "tests/hw/test_probe_negative_paths_v2.py",
        "tests/hw/test_dma_iommu_policy_v2.py",
        "tests/hw/test_acpi_boot_paths_v2.py",
        "tests/hw/test_bare_metal_smoke_v2.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M15 artifact: {rel}"

    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M15_EXECUTION_BACKLOG.md")

    assert "test-hw-matrix-v2" in makefile
    for test_name in [
        "tests/hw/test_hardware_matrix_v2.py",
        "tests/hw/test_probe_negative_paths_v2.py",
        "tests/hw/test_dma_iommu_policy_v2.py",
        "tests/hw/test_acpi_boot_paths_v2.py",
        "tests/hw/test_bare_metal_smoke_v2.py",
        "tests/hw/test_hw_gate_v2.py",
    ]:
        assert test_name in makefile

    assert "Hardware matrix v2 gate" in ci
    assert "make test-hw-matrix-v2" in ci
    assert "hw-matrix-v2-junit" in ci
    assert "Status: done" in backlog
