"""M20 aggregate gate: operability and release UX v2 wiring."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_operability_release_ux_v2_gate_wiring_and_artifacts():
    required = [
        "docs/M20_EXECUTION_BACKLOG.md",
        "docs/build/installer_recovery_baseline_v2.md",
        "docs/build/operations_runbook_v2.md",
        "docs/pkg/update_protocol_v2.md",
        "docs/pkg/rollback_policy_v2.md",
        "tools/build_installer_v2.py",
        "tools/run_upgrade_recovery_drill_v2.py",
        "tools/collect_support_bundle_v2.py",
        "tests/build/test_installer_recovery_v2.py",
        "tests/build/test_upgrade_rollback_v2.py",
        "tests/build/test_support_bundle_v2.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M20 artifact: {rel}"

    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M20_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-release-ops-v2" in makefile
    for entry in [
        "tools/build_installer_v2.py --out $(OUT)/installer-v2.json",
        "tools/run_upgrade_recovery_drill_v2.py --out $(OUT)/upgrade-recovery-v2.json",
        "tools/collect_support_bundle_v2.py --artifacts $(OUT)/installer-v2.json $(OUT)/upgrade-recovery-v2.json --out $(OUT)/support-bundle-v2.json",
        "tests/build/test_installer_recovery_v2.py",
        "tests/build/test_upgrade_rollback_v2.py",
        "tests/build/test_support_bundle_v2.py",
        "tests/build/test_operability_gate_v2.py",
    ]:
        assert entry in makefile
    assert "pytest-release-ops-v2.xml" in makefile

    assert "Operability and release UX v2 gate" in ci
    assert "make test-release-ops-v2" in ci
    assert "release-ops-v2-artifacts" in ci
    assert "out/pytest-release-ops-v2.xml" in ci
    assert "out/installer-v2.json" in ci
    assert "out/upgrade-recovery-v2.json" in ci
    assert "out/support-bundle-v2.json" in ci

    assert "Status: done" in backlog
    assert "M20" in milestones
    assert "M20" in status
    assert "M20" in readme
