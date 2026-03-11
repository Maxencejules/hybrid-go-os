"""M31 aggregate gate: release lifecycle v2 wiring and closure checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import release_branch_audit_v2 as branch_audit  # noqa: E402
import support_window_audit_v1 as support_audit  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_release_lifecycle_gate_v2_wiring_and_artifacts(tmp_path: Path):
    required = [
        "docs/M31_EXECUTION_BACKLOG.md",
        "docs/build/release_policy_v2.md",
        "docs/build/support_lifecycle_policy_v1.md",
        "docs/build/supply_chain_revalidation_policy_v1.md",
        "docs/build/release_attestation_policy_v1.md",
        "tools/release_branch_audit_v2.py",
        "tools/support_window_audit_v1.py",
        "tools/verify_sbom_provenance_v2.py",
        "tools/verify_release_attestations_v1.py",
        "tests/build/test_release_policy_v2_docs.py",
        "tests/build/test_release_branch_policy_v2.py",
        "tests/build/test_support_window_policy_v1.py",
        "tests/build/test_supply_chain_revalidation_gate_v1.py",
        "tests/build/test_release_lifecycle_gate_v2.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M31 artifact: {rel}"

    roadmap = _read("docs/M21_M34_MATURITY_PARITY_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M31_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-release-lifecycle-v2" in roadmap
    assert "test-supply-chain-revalidation-v1" in roadmap

    assert "test-release-lifecycle-v2" in makefile
    for entry in [
        "tools/release_branch_audit_v2.py --out $(OUT)/release-branch-audit-v2.json",
        "tools/support_window_audit_v1.py --out $(OUT)/support-window-audit-v1.json",
        "$(MAKE) test-supply-chain-revalidation-v1",
        "tests/build/test_release_policy_v2_docs.py",
        "tests/build/test_release_branch_policy_v2.py",
        "tests/build/test_support_window_policy_v1.py",
        "tests/build/test_release_lifecycle_gate_v2.py",
    ]:
        assert entry in makefile
    assert "pytest-release-lifecycle-v2.xml" in makefile

    assert "Release lifecycle v2 gate" in ci
    assert "make test-release-lifecycle-v2" in ci
    assert "release-lifecycle-v2-artifacts" in ci
    assert "out/pytest-release-lifecycle-v2.xml" in ci
    assert "out/release-branch-audit-v2.json" in ci
    assert "out/support-window-audit-v1.json" in ci

    assert "Supply-chain revalidation v1 gate" in ci
    assert "make test-supply-chain-revalidation-v1" in ci

    assert "Status: done" in backlog
    assert "M31" in milestones
    assert "M31" in status
    assert "docs/architecture/SOURCE_MAP.md" in readme
    assert "docs/archive/README.md" in readme

    branch_out = tmp_path / "release-branch-audit-v2.json"
    support_out = tmp_path / "support-window-audit-v1.json"

    assert branch_audit.main(["--out", str(branch_out), "--max-failures", "0"]) == 0
    assert support_audit.main(["--out", str(support_out), "--max-failures", "0"]) == 0

    branch_data = json.loads(branch_out.read_text(encoding="utf-8"))
    support_data = json.loads(support_out.read_text(encoding="utf-8"))

    assert branch_data["schema"] == "rugo.release_branch_audit.v2"
    assert branch_data["policy_id"] == "rugo.release_policy.v2"
    assert branch_data["total_failures"] == 0
    assert branch_data["meets_target"] is True

    assert support_data["schema"] == "rugo.support_window_audit.v1"
    assert support_data["policy_id"] == "rugo.support_lifecycle_policy.v1"
    assert support_data["total_failures"] == 0
    assert support_data["meets_target"] is True
