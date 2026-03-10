"""M45 PR-2: deterministic negative-path checks for matrix v6."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_hw_matrix_v6 as matrix  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _out_path(name: str) -> Path:
    path = ROOT / "out" / "pytest-m45" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    return path


def test_negative_path_contract_states_present():
    contract = _read("docs/hw/driver_lifecycle_contract_v6.md")
    for token in [
        "`probe_missing`",
        "`BLK: not found`",
        "`NET: not found`",
        "`SCSI: not found`",
        "`GPU: not found`",
        "`error_fatal`",
    ]:
        assert token in contract


def test_hw_matrix_v6_detects_scsi_negative_path_regression():
    out = _out_path("hw-matrix-v6-negative-scsi-fail.json")
    rc = matrix.main(
        [
            "--inject-failure",
            "negative_scsi_missing_deterministic",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["negative_path"]["failures"] >= 1
    assert data["negative_paths"]["scsi_probe_missing"]["deterministic"] is False


def test_hw_matrix_v6_detects_gpu_negative_path_regression():
    out = _out_path("hw-matrix-v6-negative-gpu-fail.json")
    rc = matrix.main(
        [
            "--inject-failure",
            "negative_gpu_missing_deterministic",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["negative_path"]["failures"] >= 1
    assert data["negative_paths"]["gpu_probe_missing"]["deterministic"] is False
