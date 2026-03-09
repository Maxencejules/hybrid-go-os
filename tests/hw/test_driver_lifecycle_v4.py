"""M37 PR-2: driver lifecycle v4 contract and matrix report checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_hw_matrix_v4 as matrix  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def _driver_row(data: dict, driver: str) -> dict:
    rows = [entry for entry in data["driver_lifecycle"] if entry["driver"] == driver]
    assert len(rows) == 1
    return rows[0]


def test_driver_lifecycle_contract_v4_has_required_states():
    contract = _read("docs/hw/driver_lifecycle_contract_v4.md")
    for token in [
        "Schema identifier: `rugo.driver_lifecycle_report.v4`",
        "`probe_missing`",
        "`probe_found`",
        "`init_ready`",
        "`runtime_ok`",
        "`suspend_prepare`",
        "`resume_ok`",
        "`hotplug_add`",
        "`hotplug_remove`",
        "`reset_recover`",
        "`error_recoverable`",
        "`error_fatal`",
    ]:
        assert token in contract


def test_driver_lifecycle_v4_report_is_seed_deterministic():
    first = matrix.run_matrix(seed=20260309)
    second = matrix.run_matrix(seed=20260309)
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_driver_lifecycle_v4_report_contains_required_runtime_paths():
    report = matrix.run_matrix(seed=20260309)
    assert report["schema"] == "rugo.hw_matrix_evidence.v4"
    assert report["driver_contract_id"] == "rugo.driver_lifecycle_report.v4"
    assert report["gate_pass"] is True

    required_states = {
        "probe_found",
        "init_ready",
        "runtime_ok",
        "suspend_prepare",
        "resume_ok",
        "hotplug_add",
        "hotplug_remove",
        "reset_recover",
    }
    for driver_name in ["virtio-blk-pci", "virtio-net-pci"]:
        row = _driver_row(report, driver_name)
        assert required_states.issubset(set(row["states_observed"]))
        assert row["init_failures"] == 0
        assert row["runtime_errors"] == 0
        assert row["fatal_errors"] == 0
        assert row["status"] == "pass"


def test_driver_lifecycle_v4_report_detects_runtime_regression(tmp_path: Path):
    out = tmp_path / "hw-matrix-v4-lifecycle-fail.json"
    rc = matrix.main(
        [
            "--inject-failure",
            "lifecycle_virtio_blk",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    row = _driver_row(data, "virtio-blk-pci")
    assert row["status"] == "fail"
    assert row["runtime_errors"] > 0
