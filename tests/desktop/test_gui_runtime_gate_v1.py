"""M51 aggregate gate: GUI runtime wiring and closure checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_gui_runtime_v1 as runtime  # noqa: E402
import run_toolkit_compat_v1 as compat  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _out_path(name: str) -> Path:
    path = ROOT / "out" / "pytest-m51" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    return path


def test_gui_runtime_gate_v1_wiring_and_artifacts():
    required = [
        "docs/M51_EXECUTION_BACKLOG.md",
        "docs/desktop/gui_runtime_contract_v1.md",
        "docs/desktop/toolkit_profile_v1.md",
        "docs/desktop/font_text_rendering_policy_v1.md",
        "tools/run_gui_runtime_v1.py",
        "tools/run_toolkit_compat_v1.py",
        "tests/desktop/test_gui_runtime_docs_v1.py",
        "tests/desktop/test_gui_app_launch_render_v1.py",
        "tests/desktop/test_font_text_rendering_v1.py",
        "tests/desktop/test_toolkit_event_loop_v1.py",
        "tests/desktop/test_gui_runtime_negative_v1.py",
        "tests/desktop/test_toolkit_compat_gate_v1.py",
        "tests/desktop/test_gui_runtime_gate_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M51 artifact: {rel}"

    roadmap = _read("docs/M48_M52_GUI_IMPLEMENTATION_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M51_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-gui-runtime-v1" in roadmap
    assert "test-toolkit-compat-v1" in roadmap

    assert "test-gui-runtime-v1" in makefile
    for entry in [
        "tools/run_gui_runtime_v1.py --out $(OUT)/gui-runtime-v1.json",
        "$(SUBMAKE) test-toolkit-compat-v1",
        "tests/desktop/test_gui_runtime_docs_v1.py",
        "tests/desktop/test_gui_app_launch_render_v1.py",
        "tests/desktop/test_font_text_rendering_v1.py",
        "tests/desktop/test_toolkit_event_loop_v1.py",
        "tests/desktop/test_gui_runtime_negative_v1.py",
        "tests/desktop/test_gui_runtime_gate_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-gui-runtime-v1.xml" in makefile
    assert "pytest-toolkit-compat-v1.xml" in makefile

    assert "GUI runtime v1 gate" in ci
    assert "make test-gui-runtime-v1" in ci
    assert "gui-runtime-v1-artifacts" in ci
    assert "out/pytest-gui-runtime-v1.xml" in ci
    assert "out/gui-runtime-v1.json" in ci
    assert "out/toolkit-compat-v1.json" in ci

    assert "Toolkit compatibility v1 gate" in ci
    assert "make test-toolkit-compat-v1" in ci
    assert "toolkit-compat-v1-artifacts" in ci
    assert "out/pytest-toolkit-compat-v1.xml" in ci

    assert "Status: done" in backlog
    assert "| M51 | GUI Runtime + Toolkit Bridge v1 | n/a | done |" in milestones
    assert "| **M51** GUI Runtime + Toolkit Bridge v1 | n/a | done |" in status
    assert "M0-M51: done" in readme
    assert "Latest completed GUI milestone: `M51`." in readme
    assert "M51 execution backlog (completed)" in readme

    runtime_out = _out_path("gui-runtime-gate-v1.json")
    compat_out = _out_path("toolkit-compat-gate-v1.json")

    assert runtime.main(["--seed", "20260311", "--out", str(runtime_out)]) == 0
    assert compat.main(["--seed", "20260311", "--out", str(compat_out)]) == 0

    runtime_data = json.loads(runtime_out.read_text(encoding="utf-8"))
    compat_data = json.loads(compat_out.read_text(encoding="utf-8"))

    assert runtime_data["schema"] == "rugo.gui_runtime_report.v1"
    assert runtime_data["contract_id"] == "rugo.gui_runtime_contract.v1"
    assert runtime_data["gate_pass"] is True
    assert runtime_data["total_failures"] == 0

    assert compat_data["schema"] == "rugo.toolkit_compat_report.v1"
    assert compat_data["runtime_schema"] == "rugo.gui_runtime_report.v1"
    assert compat_data["gate_pass"] is True
