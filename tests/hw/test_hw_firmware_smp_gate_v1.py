"""M43 aggregate gate: hardware/firmware/SMP v1 wiring and closure checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import collect_firmware_smp_evidence_v1 as evidence  # noqa: E402
import run_hw_matrix_v5 as matrix  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_hw_firmware_smp_gate_v1_wiring_and_artifacts(tmp_path: Path):
    required = [
        "docs/M43_EXECUTION_BACKLOG.md",
        "docs/hw/support_matrix_v5.md",
        "docs/hw/driver_lifecycle_contract_v5.md",
        "docs/hw/acpi_uefi_hardening_v3.md",
        "docs/runtime/smp_interrupt_model_v1.md",
        "tools/run_hw_matrix_v5.py",
        "tools/collect_firmware_smp_evidence_v1.py",
        "tests/hw/test_hw_matrix_docs_v5.py",
        "tests/hw/test_native_storage_driver_matrix_v1.py",
        "tests/hw/test_native_nic_driver_matrix_v1.py",
        "tests/hw/test_firmware_table_validation_v3.py",
        "tests/hw/test_smp_interrupt_baseline_v1.py",
        "tests/hw/test_native_driver_matrix_gate_v1.py",
        "tests/hw/test_hw_firmware_smp_gate_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M43 artifact: {rel}"

    roadmap = _read("docs/M40_M44_GENERAL_PURPOSE_PARITY_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M43_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-hw-firmware-smp-v1" in roadmap
    assert "test-native-driver-matrix-v1" in roadmap

    assert "test-hw-firmware-smp-v1" in makefile
    for entry in [
        "tools/run_hw_matrix_v5.py --out $(OUT)/hw-matrix-v5.json",
        "$(MAKE) test-native-driver-matrix-v1",
        "tests/hw/test_hw_matrix_docs_v5.py",
        "tests/hw/test_native_storage_driver_matrix_v1.py",
        "tests/hw/test_native_nic_driver_matrix_v1.py",
        "tests/hw/test_firmware_table_validation_v3.py",
        "tests/hw/test_smp_interrupt_baseline_v1.py",
        "tests/hw/test_hw_firmware_smp_gate_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-hw-firmware-smp-v1.xml" in makefile
    assert "pytest-native-driver-matrix-v1.xml" in makefile

    assert "Hardware firmware smp v1 gate" in ci
    assert "make test-hw-firmware-smp-v1" in ci
    assert "hw-firmware-smp-v1-artifacts" in ci
    assert "out/pytest-hw-firmware-smp-v1.xml" in ci
    assert "out/hw-matrix-v5.json" in ci
    assert "out/hw-firmware-smp-v1.json" in ci

    assert "Native driver matrix v1 gate" in ci
    assert "make test-native-driver-matrix-v1" in ci
    assert "native-driver-matrix-v1-artifacts" in ci
    assert "out/pytest-native-driver-matrix-v1.xml" in ci

    assert "Status: done" in backlog
    assert "| M43 | Hardware/Firmware Breadth + SMP v1 | n/a | done |" in milestones
    assert "| **M43** Hardware/Firmware Breadth + SMP v1 | n/a | done |" in status
    assert "M0-M43: done" in readme
    assert "M43 execution backlog (completed)" in readme

    matrix_out = tmp_path / "hw-matrix-v5.json"
    evidence_out = tmp_path / "hw-firmware-smp-v1.json"

    assert matrix.main(["--seed", "20260310", "--out", str(matrix_out)]) == 0
    assert evidence.main(["--seed", "20260310", "--out", str(evidence_out)]) == 0

    matrix_data = json.loads(matrix_out.read_text(encoding="utf-8"))
    evidence_data = json.loads(evidence_out.read_text(encoding="utf-8"))

    assert matrix_data["schema"] == "rugo.hw_matrix_evidence.v5"
    assert matrix_data["gate_pass"] is True
    assert matrix_data["total_failures"] == 0

    assert evidence_data["schema"] == "rugo.hw_firmware_smp_evidence.v1"
    assert evidence_data["firmware_hardening_id"] == "rugo.acpi_uefi_hardening.v3"
    assert evidence_data["smp_interrupt_model_id"] == "rugo.smp_interrupt_model.v1"
    assert evidence_data["gate_pass"] is True
    assert evidence_data["total_failures"] == 0
