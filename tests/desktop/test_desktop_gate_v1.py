"""M35 aggregate gate: desktop stack v1 wiring and closure checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_desktop_smoke_v1 as smoke  # noqa: E402
import run_gui_app_matrix_v1 as matrix  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_desktop_gate_v1_wiring_and_artifacts(tmp_path: Path):
    required = [
        "docs/M35_EXECUTION_BACKLOG.md",
        "docs/desktop/display_stack_contract_v1.md",
        "docs/desktop/window_manager_contract_v1.md",
        "docs/desktop/input_stack_contract_v1.md",
        "docs/desktop/desktop_profile_v1.md",
        "tools/run_desktop_smoke_v1.py",
        "tools/run_gui_app_matrix_v1.py",
        "tests/desktop/test_desktop_docs_v1.py",
        "tests/desktop/test_display_session_v1.py",
        "tests/desktop/test_input_baseline_v1.py",
        "tests/desktop/test_window_lifecycle_v1.py",
        "tests/desktop/test_gui_app_compat_v1.py",
        "tests/desktop/test_gui_app_compat_gate_v1.py",
        "tests/desktop/test_desktop_gate_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M35 artifact: {rel}"

    roadmap = _read("docs/M35_M39_GENERAL_PURPOSE_EXPANSION_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M35_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-desktop-stack-v1" in roadmap
    assert "test-gui-app-compat-v1" in roadmap

    assert "test-desktop-stack-v1" in makefile
    for entry in [
        "tools/run_desktop_smoke_v1.py --out $(OUT)/desktop-smoke-v1.json",
        "$(MAKE) test-gui-app-compat-v1",
        "tests/desktop/test_desktop_docs_v1.py",
        "tests/desktop/test_display_session_v1.py",
        "tests/desktop/test_input_baseline_v1.py",
        "tests/desktop/test_window_lifecycle_v1.py",
        "tests/desktop/test_desktop_gate_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-desktop-stack-v1.xml" in makefile
    assert "pytest-gui-app-compat-v1.xml" in makefile

    assert "Desktop stack v1 gate" in ci
    assert "make test-desktop-stack-v1" in ci
    assert "desktop-stack-v1-artifacts" in ci
    assert "out/pytest-desktop-stack-v1.xml" in ci
    assert "out/desktop-smoke-v1.json" in ci

    assert "GUI app compatibility v1 gate" in ci
    assert "make test-gui-app-compat-v1" in ci
    assert "gui-app-compat-v1-artifacts" in ci
    assert "out/pytest-gui-app-compat-v1.xml" in ci
    assert "out/gui-app-matrix-v1.json" in ci

    assert "Status: done" in backlog
    assert "M35" in milestones
    assert "M35" in status
    assert "M35" in readme

    smoke_out = tmp_path / "desktop-smoke-v1.json"
    matrix_out = tmp_path / "gui-app-matrix-v1.json"

    assert smoke.main(["--seed", "20260309", "--out", str(smoke_out)]) == 0
    assert matrix.main(["--seed", "20260309", "--out", str(matrix_out)]) == 0

    smoke_data = json.loads(smoke_out.read_text(encoding="utf-8"))
    matrix_data = json.loads(matrix_out.read_text(encoding="utf-8"))

    assert smoke_data["schema"] == "rugo.desktop_smoke_report.v1"
    assert smoke_data["policy_id"] == "rugo.desktop_profile.v1"
    assert smoke_data["total_failures"] == 0
    assert smoke_data["gate_pass"] is True

    assert matrix_data["schema"] == "rugo.gui_app_matrix_report.v1"
    assert matrix_data["profile_id"] == "rugo.desktop_profile.v1"
    assert matrix_data["total_failures"] == 0
    assert matrix_data["gate_pass"] is True

