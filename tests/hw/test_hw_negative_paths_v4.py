"""M37 PR-2: deterministic negative-path checks for matrix v4."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_hw_matrix_v4 as matrix  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _check(data: dict, check_id: str) -> dict:
    rows = [entry for entry in data["checks"] if entry["check_id"] == check_id]
    assert len(rows) == 1
    return rows[0]


def test_block_probe_missing_device_v4(qemu_serial_blk_missing):
    """Missing block device must keep deterministic v4 failure marker."""
    out = qemu_serial_blk_missing.stdout
    assert "BLK: not found" in out, (
        f"Missing deterministic block probe marker for v4. Got:\n{out}"
    )


def test_net_probe_missing_device_v4(qemu_serial_net_missing):
    """Missing NIC must keep deterministic v4 failure marker."""
    out = qemu_serial_net_missing.stdout
    assert "NET: not found" in out, (
        f"Missing deterministic net probe marker for v4. Got:\n{out}"
    )


def test_negative_path_contract_states_present():
    """Driver lifecycle v4 contract must keep explicit negative-path semantics."""
    contract = _read("docs/hw/driver_lifecycle_contract_v4.md")
    for token in [
        "`probe_missing`",
        "`BLK: not found`",
        "`NET: not found`",
        "`error_fatal`",
    ]:
        assert token in contract


def test_hw_matrix_v4_detects_negative_path_regression(tmp_path: Path):
    out = tmp_path / "hw-matrix-v4-negative-fail.json"
    rc = matrix.main(
        [
            "--inject-failure",
            "negative_blk_missing_deterministic",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["negative_path"]["failures"] >= 1
    assert _check(data, "negative_blk_missing_deterministic")["pass"] is False
    assert data["negative_paths"]["block_probe_missing"]["deterministic"] is False


def test_hw_matrix_v4_rejects_unknown_check_id(tmp_path: Path):
    out = tmp_path / "hw-matrix-v4-negative-error.json"
    rc = matrix.main(
        [
            "--inject-failure",
            "unknown_negative_path_check",
            "--out",
            str(out),
        ]
    )
    assert rc == 2
    assert not out.exists()
