"""M45 PR-2: deterministic virtio-scsi checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_hw_matrix_v6 as matrix  # noqa: E402


def _coverage_entry(data: dict, device: str, profile: str) -> dict:
    rows = [
        entry
        for entry in data["device_class_coverage"]
        if entry["device"] == device and entry["profile"] == profile
    ]
    assert len(rows) == 1
    return rows[0]


def _driver_row(data: dict, driver: str, profile: str) -> dict:
    rows = [
        entry
        for entry in data["driver_lifecycle"]
        if entry["driver"] == driver and entry["profile"] == profile
    ]
    assert len(rows) == 1
    return rows[0]


def _out_path(name: str) -> Path:
    path = ROOT / "out" / "pytest-m45" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    return path


def test_virtio_scsi_v1_schema_and_pass():
    out = _out_path("hw-matrix-v6-scsi.json")
    rc = matrix.main(["--seed", "20260310", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.hw_matrix_evidence.v6"
    assert data["gate_pass"] is True
    assert data["summary"]["matrix_scsi"]["pass"] is True
    assert _coverage_entry(data, "virtio-scsi-pci", "modern")["status"] == "pass"
    row = _driver_row(data, "virtio-scsi-pci", "modern")
    assert row["status"] == "pass"
    assert "runtime_ok" in row["states_observed"]


def test_virtio_scsi_v1_detects_regression():
    out = _out_path("hw-matrix-v6-scsi-fail.json")
    rc = matrix.main(
        [
            "--inject-failure",
            "lifecycle_virtio_scsi",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["lifecycle"]["failures"] >= 1
    assert _coverage_entry(data, "virtio-scsi-pci", "modern")["status"] == "pass"
    assert _driver_row(data, "virtio-scsi-pci", "modern")["status"] == "fail"
