"""M45 PR-2: deterministic virtio-gpu framebuffer checks."""

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


def test_virtio_gpu_framebuffer_v1_schema_and_pass():
    out = _out_path("hw-matrix-v6-gpu.json")
    rc = matrix.main(["--seed", "20260310", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.hw_matrix_evidence.v6"
    assert data["display_class"] == "virtio-gpu-pci"
    assert data["desktop_display_checks"]["bridge_pass"] is True
    assert data["summary"]["matrix_gpu"]["pass"] is True
    assert _coverage_entry(data, "virtio-gpu-pci", "modern")["status"] == "pass"
    row = _driver_row(data, "virtio-gpu-pci", "modern")
    assert row["status"] == "pass"
    assert "framebuffer_console_present" in row["states_observed"]
    assert "display_scanout_ready" in row["states_observed"]


def test_virtio_gpu_framebuffer_v1_tied_to_desktop_bridge():
    out = _out_path("hw-matrix-v6-gpu-fail.json")
    rc = matrix.main(
        [
            "--inject-failure",
            "desktop_display_bridge",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["desktop_display_checks"]["bridge_pass"] is False
    assert _coverage_entry(data, "virtio-gpu-pci", "modern")["status"] == "fail"
    assert _driver_row(data, "virtio-gpu-pci", "modern")["status"] == "fail"
