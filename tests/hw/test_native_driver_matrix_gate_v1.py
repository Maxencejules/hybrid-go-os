"""M43 aggregate sub-gate: native driver matrix v1 wiring and artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import collect_firmware_smp_evidence_v1 as evidence  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_native_driver_matrix_gate_v1_wiring_and_artifacts(tmp_path: Path):
    required = [
        "docs/M43_EXECUTION_BACKLOG.md",
        "docs/hw/support_matrix_v5.md",
        "docs/hw/driver_lifecycle_contract_v5.md",
        "tools/collect_firmware_smp_evidence_v1.py",
        "tests/hw/test_hw_matrix_docs_v5.py",
        "tests/hw/test_native_storage_driver_matrix_v1.py",
        "tests/hw/test_native_nic_driver_matrix_v1.py",
        "tests/hw/test_firmware_table_validation_v3.py",
        "tests/hw/test_smp_interrupt_baseline_v1.py",
        "tests/hw/test_native_driver_matrix_gate_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M43 native sub-gate artifact: {rel}"

    roadmap = _read("docs/M40_M44_GENERAL_PURPOSE_PARITY_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M43_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-native-driver-matrix-v1" in roadmap

    assert "test-native-driver-matrix-v1" in makefile
    for entry in [
        "tools/collect_firmware_smp_evidence_v1.py --out $(OUT)/hw-firmware-smp-v1.json",
        "tests/hw/test_hw_matrix_docs_v5.py",
        "tests/hw/test_native_storage_driver_matrix_v1.py",
        "tests/hw/test_native_nic_driver_matrix_v1.py",
        "tests/hw/test_firmware_table_validation_v3.py",
        "tests/hw/test_smp_interrupt_baseline_v1.py",
        "tests/hw/test_native_driver_matrix_gate_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-native-driver-matrix-v1.xml" in makefile

    assert "Native driver matrix v1 gate" in ci
    assert "make test-native-driver-matrix-v1" in ci
    assert "native-driver-matrix-v1-artifacts" in ci
    assert "out/pytest-native-driver-matrix-v1.xml" in ci
    assert "out/hw-firmware-smp-v1.json" in ci

    assert "Status: done" in backlog
    assert "M43" in milestones
    assert "M43" in status
    assert "M43 execution backlog (completed)" in readme

    out = tmp_path / "hw-firmware-smp-v1.json"
    assert evidence.main(["--seed", "20260310", "--out", str(out)]) == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["schema"] == "rugo.hw_firmware_smp_evidence.v1"
    assert report["firmware_hardening_id"] == "rugo.acpi_uefi_hardening.v3"
    assert report["smp_interrupt_model_id"] == "rugo.smp_interrupt_model.v1"
    assert report["gate_pass"] is True
    assert report["total_failures"] == 0
    assert report["native_driver_matrix"]["storage"]["checks_pass"] is True
    assert report["native_driver_matrix"]["network"]["checks_pass"] is True
