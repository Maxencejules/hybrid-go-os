"""M20 acceptance: installer and recovery v2 contracts."""

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import build_installer_v2 as installer_tool  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_installer_and_runbook_docs_present_with_contract_tokens():
    required = [
        "docs/M20_EXECUTION_BACKLOG.md",
        "docs/build/installer_recovery_baseline_v2.md",
        "docs/build/operations_runbook_v2.md",
        "tools/build_installer_v2.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M20 PR-1 artifact: {rel}"

    baseline = _read("docs/build/installer_recovery_baseline_v2.md")
    runbook = _read("docs/build/operations_runbook_v2.md")

    for token in [
        "schema: `rugo.installer_contract.v2`",
        "rollback to the last trusted sequence",
        "make test-release-ops-v2",
    ]:
        assert token in baseline

    for token in [
        "python tools/build_installer_v2.py --out out/installer-v2.json",
        "python tools/run_upgrade_recovery_drill_v2.py --out out/upgrade-recovery-v2.json",
        "python tools/collect_support_bundle_v2.py",
    ]:
        assert token in runbook


def test_build_installer_v2_schema(tmp_path: Path):
    out = tmp_path / "installer-v2.json"
    rc = installer_tool.main(
        [
            "--channel",
            "stable",
            "--version",
            "2.0.0",
            "--build-sequence",
            "12",
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    assert out.is_file()

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.installer_contract.v2"
    assert data["selected_channel"] == "stable"
    assert data["version"] == "2.0.0"
    assert data["build_sequence"] == 12
    assert data["installer_profile"]["mode"] == "offline-first"
    assert data["recovery_profile"]["rollback_supported"] is True
    assert "sha256" in data["preflight_checks"]
