"""M36 aggregate sub-gate: POSIX gap closure v1 wiring and artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_posix_gap_report_v1 as gap  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_posix_gap_closure_gate_v1_wiring_and_artifacts(tmp_path: Path):
    required = [
        "docs/M36_EXECUTION_BACKLOG.md",
        "docs/abi/compat_profile_v4.md",
        "docs/runtime/syscall_coverage_matrix_v3.md",
        "tools/run_posix_gap_report_v1.py",
        "tests/compat/test_posix_gap_closure_v1.py",
        "tests/compat/test_deferred_surface_behavior_v1.py",
        "tests/compat/test_posix_gap_closure_gate_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M36 POSIX artifact: {rel}"

    roadmap = _read("docs/M35_M39_GENERAL_PURPOSE_EXPANSION_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M36_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-posix-gap-closure-v1" in roadmap

    assert "test-posix-gap-closure-v1" in makefile
    for entry in [
        "tools/run_posix_gap_report_v1.py --out $(OUT)/posix-gap-report-v1.json",
        "tests/compat/test_posix_gap_closure_v1.py",
        "tests/compat/test_deferred_surface_behavior_v1.py",
        "tests/compat/test_posix_gap_closure_gate_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-posix-gap-closure-v1.xml" in makefile

    assert "POSIX gap closure v1 gate" in ci
    assert "make test-posix-gap-closure-v1" in ci
    assert "posix-gap-closure-v1-artifacts" in ci
    assert "out/pytest-posix-gap-closure-v1.xml" in ci
    assert "out/posix-gap-report-v1.json" in ci

    assert "Status: done" in backlog
    assert "M36" in milestones
    assert "M36" in status
    assert "docs/architecture/SOURCE_MAP.md" in readme
    assert "docs/archive/README.md" in readme

    out = tmp_path / "posix-gap-report-v1.json"
    assert gap.main(["--seed", "20260309", "--out", str(out)]) == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["schema"] == "rugo.posix_gap_report.v1"
    assert report["profile_id"] == "rugo.compat_profile.v4"
    assert report["gate_pass"] is True
    assert report["total_failures"] == 0
