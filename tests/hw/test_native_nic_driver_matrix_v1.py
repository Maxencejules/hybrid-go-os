"""M43 PR-2: deterministic native NIC driver matrix checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_hw_matrix_v5 as matrix  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _coverage_entry(data: dict, device: str) -> dict:
    rows = [entry for entry in data["device_class_coverage"] if entry["device"] == device]
    assert len(rows) == 1
    return rows[0]


def _driver_row(data: dict, driver: str) -> dict:
    rows = [entry for entry in data["driver_lifecycle"] if entry["driver"] == driver]
    assert len(rows) == 1
    return rows[0]


def test_native_nic_driver_contract_v5_has_required_tokens():
    contract = _read("docs/hw/driver_lifecycle_contract_v5.md")
    for token in [
        "Schema identifier: `rugo.driver_lifecycle_report.v5`",
        "`irq_vector_bound`",
        "`irq_vector_retarget`",
        "`cpu_affinity_balance`",
        "`virtio-net-pci`, `e1000`, `rtl8139`",
    ]:
        assert token in contract


def test_native_nic_driver_matrix_v1_schema_and_pass(tmp_path: Path):
    out = tmp_path / "hw-matrix-v5-nic.json"
    rc = matrix.main(["--seed", "20260310", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.hw_matrix_evidence.v5"
    assert data["gate_pass"] is True
    assert data["summary"]["coverage_network"]["pass"] is True
    assert data["native_driver_matrix"]["network"]["checks_pass"] is True
    assert data["native_driver_matrix"]["network"]["pass_rate"] == 1.0
    assert _coverage_entry(data, "e1000")["status"] == "pass"
    assert _coverage_entry(data, "rtl8139")["status"] == "pass"
    assert _driver_row(data, "e1000")["status"] == "pass"
    assert _driver_row(data, "rtl8139")["status"] == "pass"


def test_native_nic_driver_matrix_v1_detects_rtl8139_regression(tmp_path: Path):
    out = tmp_path / "hw-matrix-v5-nic-fail.json"
    rc = matrix.main(
        [
            "--inject-failure",
            "coverage_network_rtl8139",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["coverage_network"]["failures"] >= 1
    assert data["summary"]["native"]["failures"] >= 1
    assert _coverage_entry(data, "rtl8139")["status"] == "fail"
    assert _driver_row(data, "rtl8139")["status"] == "fail"
    assert data["native_driver_matrix"]["network"]["checks_pass"] is False
    assert data["native_driver_matrix"]["network"]["pass_rate"] < 1.0
