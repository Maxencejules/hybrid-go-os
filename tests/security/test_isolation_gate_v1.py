"""M42 aggregate gate: isolation baseline v1 wiring and closure checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_isolation_campaign_v1 as isolation  # noqa: E402
import run_resource_control_campaign_v1 as resource_control  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_isolation_gate_v1_wiring_and_artifacts(tmp_path: Path):
    required = [
        "docs/M42_EXECUTION_BACKLOG.md",
        "docs/abi/namespace_cgroup_contract_v1.md",
        "docs/security/isolation_profile_v1.md",
        "docs/runtime/resource_control_policy_v1.md",
        "tools/run_isolation_campaign_v1.py",
        "tools/run_resource_control_campaign_v1.py",
        "tests/security/test_isolation_docs_v1.py",
        "tests/security/test_namespace_baseline_v1.py",
        "tests/security/test_cgroup_baseline_v1.py",
        "tests/security/test_isolation_escape_negative_v1.py",
        "tests/runtime/test_resource_control_policy_v1.py",
        "tests/security/test_namespace_cgroup_gate_v1.py",
        "tests/security/test_isolation_gate_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M42 artifact: {rel}"

    roadmap = _read("docs/M40_M44_GENERAL_PURPOSE_PARITY_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M42_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-isolation-baseline-v1" in roadmap
    assert "test-namespace-cgroup-v1" in roadmap

    assert "test-isolation-baseline-v1" in makefile
    for entry in [
        "tools/run_isolation_campaign_v1.py --out $(OUT)/isolation-campaign-v1.json",
        "$(MAKE) test-namespace-cgroup-v1",
        "tests/security/test_isolation_docs_v1.py",
        "tests/security/test_namespace_baseline_v1.py",
        "tests/security/test_cgroup_baseline_v1.py",
        "tests/security/test_isolation_escape_negative_v1.py",
        "tests/security/test_isolation_gate_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-isolation-baseline-v1.xml" in makefile
    assert "pytest-namespace-cgroup-v1.xml" in makefile

    assert "Isolation baseline v1 gate" in ci
    assert "make test-isolation-baseline-v1" in ci
    assert "isolation-baseline-v1-artifacts" in ci
    assert "out/pytest-isolation-baseline-v1.xml" in ci
    assert "out/isolation-campaign-v1.json" in ci

    assert "Namespace cgroup v1 gate" in ci
    assert "make test-namespace-cgroup-v1" in ci
    assert "namespace-cgroup-v1-artifacts" in ci
    assert "out/pytest-namespace-cgroup-v1.xml" in ci
    assert "out/resource-control-v1.json" in ci

    assert "Status: done" in backlog
    assert "| M42 | Isolation + Namespace Baseline v1 | n/a | done |" in milestones
    assert (
        "| **M42** Isolation + Namespace Baseline v1 | n/a | done |"
        in status
    )
    assert "M0-M42: done" in readme
    assert "M42 execution backlog (completed)" in readme

    isolation_out = tmp_path / "isolation-campaign-v1.json"
    resource_out = tmp_path / "resource-control-v1.json"

    assert isolation.main(["--seed", "20260310", "--out", str(isolation_out)]) == 0
    assert (
        resource_control.main(["--seed", "20260310", "--out", str(resource_out)])
        == 0
    )

    isolation_data = json.loads(isolation_out.read_text(encoding="utf-8"))
    resource_data = json.loads(resource_out.read_text(encoding="utf-8"))

    assert isolation_data["schema"] == "rugo.isolation_campaign_report.v1"
    assert isolation_data["isolation_profile_id"] == "rugo.isolation_profile.v1"
    assert isolation_data["gate_pass"] is True
    assert isolation_data["total_failures"] == 0

    assert resource_data["schema"] == "rugo.resource_control_report.v1"
    assert resource_data["policy_id"] == "rugo.resource_control_policy.v1"
    assert resource_data["gate_pass"] is True
    assert resource_data["total_failures"] == 0
