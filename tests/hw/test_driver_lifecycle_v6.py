"""M45 PR-2: driver lifecycle v6 contract and matrix report checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_hw_matrix_v6 as matrix  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


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


def test_driver_lifecycle_contract_v6_has_required_states():
    contract = _read("docs/hw/driver_lifecycle_contract_v6.md")
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
    ]:
        assert token in contract


def test_driver_lifecycle_v6_report_is_seed_deterministic():
    first = matrix.run_matrix(seed=20260310)
    second = matrix.run_matrix(seed=20260310)
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_driver_lifecycle_v6_report_contains_required_runtime_paths():
    report = matrix.run_matrix(seed=20260310)
    assert report["schema"] == "rugo.hw_matrix_evidence.v6"
    assert report["driver_contract_id"] == "rugo.driver_lifecycle_report.v6"
    assert report["gate_pass"] is True

    required_states = {
        "probe_found",
        "init_ready",
        "runtime_ok",
        "irq_vector_bound",
        "irq_vector_retarget",
        "cpu_affinity_balance",
        "reset_recover",
    }
    for driver_name in ["virtio-blk-pci", "virtio-net-pci", "virtio-scsi-pci"]:
        row = _driver_row(report, driver_name, "modern")
        assert required_states.issubset(set(row["states_observed"]))
        assert row["init_failures"] == 0
        assert row["runtime_errors"] == 0
        assert row["fatal_errors"] == 0
        assert row["status"] == "pass"

    gpu_row = _driver_row(report, "virtio-gpu-pci", "modern")
    assert required_states.issubset(set(gpu_row["states_observed"]))
    assert "framebuffer_console_present" in gpu_row["states_observed"]
    assert "display_scanout_ready" in gpu_row["states_observed"]
    assert gpu_row["status"] == "pass"


def test_driver_lifecycle_v6_detects_runtime_regression():
    out = _out_path("hw-matrix-v6-lifecycle-fail.json")
    rc = matrix.main(
        [
            "--inject-failure",
            "lifecycle_virtio_gpu",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    row = _driver_row(data, "virtio-gpu-pci", "modern")
    assert row["status"] == "fail"
    assert row["runtime_errors"] > 0
