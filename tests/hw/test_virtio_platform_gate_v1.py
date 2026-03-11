"""M45 aggregate sub-gate: virtio platform v1 wiring and artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_desktop_smoke_v1 as smoke  # noqa: E402
import run_hw_matrix_v6 as matrix  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _out_path(name: str) -> Path:
    path = ROOT / "out" / "pytest-m45" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    return path


def test_virtio_platform_gate_v1_wiring_and_artifacts():
    required = [
        "docs/M45_EXECUTION_BACKLOG.md",
        "docs/hw/support_matrix_v6.md",
        "docs/hw/driver_lifecycle_contract_v6.md",
        "docs/hw/virtio_platform_profile_v1.md",
        "docs/desktop/display_stack_contract_v1.md",
        "tools/run_hw_matrix_v6.py",
        "tools/run_desktop_smoke_v1.py",
        "tests/hw/test_hw_matrix_docs_v6.py",
        "tests/hw/test_virtio_platform_profile_v1.py",
        "tests/desktop/test_display_device_bridge_v1.py",
        "tests/hw/test_virtio_platform_gate_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M45 sub-gate artifact: {rel}"

    roadmap = _read("docs/M45_M47_HARDWARE_EXPANSION_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M45_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-virtio-platform-v1" in roadmap

    assert "test-virtio-platform-v1" in makefile
    for entry in [
        "tools/run_hw_matrix_v6.py --out $(OUT)/hw-matrix-v6.json",
        "tools/run_desktop_smoke_v1.py --out $(OUT)/desktop-smoke-v1.json",
        "tests/hw/test_hw_matrix_docs_v6.py",
        "tests/hw/test_virtio_platform_profile_v1.py",
        "tests/desktop/test_display_device_bridge_v1.py",
        "tests/hw/test_virtio_platform_gate_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-virtio-platform-v1.xml" in makefile

    assert "Virtio platform v1 shadow gate" in ci
    assert "make test-virtio-platform-v1" in ci
    assert "virtio-platform-v1-artifacts" in ci
    assert "out/pytest-virtio-platform-v1.xml" in ci
    assert "out/hw-matrix-v6.json" in ci
    assert "out/desktop-smoke-v1.json" in ci

    assert "Status: done" in backlog
    assert "| M45 | Modern Virtual Platform Parity v1 | n/a | done |" in milestones
    assert "| **M45** Modern Virtual Platform Parity v1 | n/a | done |" in status
    assert "docs/architecture/SOURCE_MAP.md" in readme
    assert "docs/archive/README.md" in readme

    matrix_out = _out_path("virtio-platform-hw-matrix-v6.json")
    smoke_out = _out_path("virtio-platform-desktop-smoke-v1.json")

    assert matrix.main(["--seed", "20260310", "--out", str(matrix_out)]) == 0
    assert smoke.main(["--seed", "20260309", "--out", str(smoke_out)]) == 0

    matrix_data = json.loads(matrix_out.read_text(encoding="utf-8"))
    smoke_data = json.loads(smoke_out.read_text(encoding="utf-8"))

    assert matrix_data["schema"] == "rugo.hw_matrix_evidence.v6"
    assert matrix_data["virtio_platform_profile_id"] == "rugo.virtio_platform_profile.v1"
    assert matrix_data["desktop_display_checks"]["bridge_pass"] is True
    assert matrix_data["gate_pass"] is True

    assert smoke_data["schema"] == "rugo.desktop_smoke_report.v1"
    assert smoke_data["display_class"] == "virtio-gpu-pci"
    assert smoke_data["desktop_display_checks"]["bridge_pass"] is True
    assert smoke_data["gate_pass"] is True
