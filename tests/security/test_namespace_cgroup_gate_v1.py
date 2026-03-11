"""M42 aggregate sub-gate: namespace/cgroup v1 wiring and artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_resource_control_campaign_v1 as resource_control  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_namespace_cgroup_gate_v1_wiring_and_artifacts(tmp_path: Path):
    required = [
        "docs/M42_EXECUTION_BACKLOG.md",
        "docs/abi/namespace_cgroup_contract_v1.md",
        "docs/runtime/resource_control_policy_v1.md",
        "tools/run_resource_control_campaign_v1.py",
        "tests/security/test_isolation_docs_v1.py",
        "tests/security/test_namespace_baseline_v1.py",
        "tests/security/test_cgroup_baseline_v1.py",
        "tests/security/test_isolation_escape_negative_v1.py",
        "tests/runtime/test_resource_control_policy_v1.py",
        "tests/security/test_namespace_cgroup_gate_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M42 namespace/cgroup artifact: {rel}"

    roadmap = _read("docs/M40_M44_GENERAL_PURPOSE_PARITY_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M42_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-namespace-cgroup-v1" in roadmap

    assert "test-namespace-cgroup-v1" in makefile
    for entry in [
        "tools/run_resource_control_campaign_v1.py --out $(OUT)/resource-control-v1.json",
        "tests/security/test_isolation_docs_v1.py",
        "tests/security/test_namespace_baseline_v1.py",
        "tests/security/test_cgroup_baseline_v1.py",
        "tests/security/test_isolation_escape_negative_v1.py",
        "tests/runtime/test_resource_control_policy_v1.py",
        "tests/security/test_namespace_cgroup_gate_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-namespace-cgroup-v1.xml" in makefile

    assert "Namespace cgroup v1 gate" in ci
    assert "make test-namespace-cgroup-v1" in ci
    assert "namespace-cgroup-v1-artifacts" in ci
    assert "out/pytest-namespace-cgroup-v1.xml" in ci
    assert "out/resource-control-v1.json" in ci

    assert "Status: done" in backlog
    assert "M42" in milestones
    assert "M42" in status
    assert "docs/architecture/SOURCE_MAP.md" in readme
    assert "docs/archive/README.md" in readme

    out = tmp_path / "resource-control-v1.json"
    assert resource_control.main(["--seed", "20260310", "--out", str(out)]) == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["schema"] == "rugo.resource_control_report.v1"
    assert report["policy_id"] == "rugo.resource_control_policy.v1"
    assert report["gate_pass"] is True
    assert report["total_failures"] == 0
