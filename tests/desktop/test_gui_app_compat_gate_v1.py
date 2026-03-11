"""M35 aggregate sub-gate: GUI app compatibility v1 wiring and artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_gui_app_matrix_v1 as matrix  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_gui_app_compat_gate_v1_wiring_and_artifacts(tmp_path: Path):
    required = [
        "docs/M35_EXECUTION_BACKLOG.md",
        "docs/desktop/desktop_profile_v1.md",
        "tools/run_gui_app_matrix_v1.py",
        "tests/desktop/test_gui_app_compat_v1.py",
        "tests/desktop/test_gui_app_compat_gate_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M35 GUI artifact: {rel}"

    roadmap = _read("docs/M35_M39_GENERAL_PURPOSE_EXPANSION_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M35_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-gui-app-compat-v1" in roadmap

    assert "test-gui-app-compat-v1" in makefile
    for entry in [
        "tools/run_gui_app_matrix_v1.py --out $(OUT)/gui-app-matrix-v1.json",
        "tests/desktop/test_gui_app_compat_v1.py",
        "tests/desktop/test_gui_app_compat_gate_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-gui-app-compat-v1.xml" in makefile

    assert "GUI app compatibility v1 gate" in ci
    assert "make test-gui-app-compat-v1" in ci
    assert "gui-app-compat-v1-artifacts" in ci
    assert "out/pytest-gui-app-compat-v1.xml" in ci
    assert "out/gui-app-matrix-v1.json" in ci

    assert "Status: done" in backlog
    assert "M35" in milestones
    assert "M35" in status
    assert "docs/architecture/SOURCE_MAP.md" in readme
    assert "docs/archive/README.md" in readme

    out = tmp_path / "gui-app-matrix-v1.json"
    assert matrix.main(["--seed", "20260309", "--out", str(out)]) == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["schema"] == "rugo.gui_app_matrix_report.v1"
    assert report["profile_id"] == "rugo.desktop_profile.v1"
    assert report["tier_schema"] == "rugo.gui_app_tiers.v1"
    assert report["gate_pass"] is True
    assert report["total_failures"] == 0
