"""M32 aggregate gate: conformance v1 wiring and closure checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_conformance_suite_v1 as conformance_tool  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_conformance_gate_v1_wiring_and_artifacts(tmp_path: Path):
    required = [
        "docs/M32_EXECUTION_BACKLOG.md",
        "docs/runtime/profile_conformance_v1.md",
        "tools/run_conformance_suite_v1.py",
        "tests/runtime/test_profile_conformance_docs_v1.py",
        "tests/runtime/test_server_profile_v1.py",
        "tests/runtime/test_dev_profile_v1.py",
        "tests/runtime/test_conformance_gate_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M32 artifact: {rel}"

    roadmap = _read("docs/M21_M34_MATURITY_PARITY_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M32_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-conformance-v1" in roadmap

    assert "test-conformance-v1" in makefile
    for entry in [
        "tools/run_conformance_suite_v1.py --seed 20260309 --out $(OUT)/conformance-v1.json",
        "tests/runtime/test_profile_conformance_docs_v1.py",
        "tests/runtime/test_server_profile_v1.py",
        "tests/runtime/test_dev_profile_v1.py",
        "tests/runtime/test_conformance_gate_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-conformance-v1.xml" in makefile

    assert "Conformance v1 gate" in ci
    assert "make test-conformance-v1" in ci
    assert "conformance-v1-artifacts" in ci
    assert "out/pytest-conformance-v1.xml" in ci
    assert "out/conformance-v1.json" in ci

    assert "Status: done" in backlog
    assert "M32" in milestones
    assert "M32" in status
    assert "docs/architecture/SOURCE_MAP.md" in readme
    assert "docs/archive/README.md" in readme

    report_out = tmp_path / "conformance-v1.json"
    assert conformance_tool.main(["--seed", "20260309", "--out", str(report_out)]) == 0
    report = json.loads(report_out.read_text(encoding="utf-8"))
    assert report["schema"] == "rugo.profile_conformance_report.v1"
    assert report["policy_id"] == "rugo.profile_conformance_policy.v1"
    assert report["profile_schema"] == "rugo.profile_requirement_set.v1"
    assert set(report["checked_profiles"]) == {
        "server_v1",
        "developer_v1",
        "appliance_v1",
    }
    assert report["gate_pass"] is True
    assert report["total_failures"] == 0
