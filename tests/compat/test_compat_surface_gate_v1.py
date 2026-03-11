"""M36 aggregate gate: compatibility surface v1 wiring and closure checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_compat_surface_campaign_v1 as campaign  # noqa: E402
import run_posix_gap_report_v1 as gap  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_compat_surface_gate_v1_wiring_and_artifacts(tmp_path: Path):
    required = [
        "docs/M36_EXECUTION_BACKLOG.md",
        "docs/abi/compat_profile_v4.md",
        "docs/runtime/syscall_coverage_matrix_v3.md",
        "docs/abi/process_model_v3.md",
        "docs/abi/socket_family_expansion_v1.md",
        "tools/run_compat_surface_campaign_v1.py",
        "tools/run_posix_gap_report_v1.py",
        "tests/compat/test_compat_docs_v4.py",
        "tests/compat/test_posix_gap_closure_v1.py",
        "tests/compat/test_process_model_v3.py",
        "tests/compat/test_socket_family_expansion_v1.py",
        "tests/compat/test_deferred_surface_behavior_v1.py",
        "tests/compat/test_posix_gap_closure_gate_v1.py",
        "tests/compat/test_compat_surface_gate_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M36 artifact: {rel}"

    roadmap = _read("docs/M35_M39_GENERAL_PURPOSE_EXPANSION_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M36_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-compat-surface-v1" in roadmap
    assert "test-posix-gap-closure-v1" in roadmap

    assert "test-compat-surface-v1" in makefile
    for entry in [
        "tools/run_compat_surface_campaign_v1.py --out $(OUT)/compat-surface-v1.json",
        "$(MAKE) test-posix-gap-closure-v1",
        "tests/compat/test_compat_docs_v4.py",
        "tests/compat/test_posix_gap_closure_v1.py",
        "tests/compat/test_process_model_v3.py",
        "tests/compat/test_socket_family_expansion_v1.py",
        "tests/compat/test_deferred_surface_behavior_v1.py",
        "tests/compat/test_compat_surface_gate_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-compat-surface-v1.xml" in makefile

    assert "Compatibility surface v1 gate" in ci
    assert "make test-compat-surface-v1" in ci
    assert "compat-surface-v1-artifacts" in ci
    assert "out/pytest-compat-surface-v1.xml" in ci
    assert "out/compat-surface-v1.json" in ci

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

    surface_out = tmp_path / "compat-surface-v1.json"
    gap_out = tmp_path / "posix-gap-report-v1.json"

    assert campaign.main(["--seed", "20260309", "--out", str(surface_out)]) == 0
    assert gap.main(["--seed", "20260309", "--out", str(gap_out)]) == 0

    surface_data = json.loads(surface_out.read_text(encoding="utf-8"))
    gap_data = json.loads(gap_out.read_text(encoding="utf-8"))

    assert surface_data["schema"] == "rugo.compat_surface_campaign_report.v1"
    assert surface_data["profile_id"] == "rugo.compat_profile.v4"
    assert surface_data["gate_pass"] is True
    assert surface_data["total_failures"] == 0

    assert gap_data["schema"] == "rugo.posix_gap_report.v1"
    assert gap_data["profile_id"] == "rugo.compat_profile.v4"
    assert gap_data["gate_pass"] is True
    assert gap_data["total_failures"] == 0
