"""M20 acceptance: support bundle v2 schema and evidence wiring."""

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import build_installer_v2 as installer_tool  # noqa: E402
import collect_support_bundle_v2 as bundle_tool  # noqa: E402
import run_upgrade_recovery_drill_v2 as drill_tool  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_support_bundle_runbook_tokens():
    text = _read("docs/build/operations_runbook_v2.md")
    for token in [
        "Collect support bundle",
        "out/support-bundle-v2.json",
        "Incident triage checklist",
    ]:
        assert token in text


def test_collect_support_bundle_v2_schema(tmp_path: Path):
    installer_out = tmp_path / "installer-v2.json"
    drill_out = tmp_path / "upgrade-recovery-v2.json"
    bundle_out = tmp_path / "support-bundle-v2.json"

    assert installer_tool.main(["--out", str(installer_out)]) == 0
    assert drill_tool.main(["--out", str(drill_out)]) == 0
    assert (
        bundle_tool.main(
            [
                "--artifacts",
                str(installer_out),
                str(drill_out),
                "--out",
                str(bundle_out),
            ]
        )
        == 0
    )

    data = json.loads(bundle_out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.support_bundle.v2"
    assert data["triage"]["runbook"] == "docs/build/operations_runbook_v2.md"
    assert data["triage"]["requires_rollback_context"] is True
    assert len(data["evidence"]) == 2
    for entry in data["evidence"]:
        assert len(entry["sha256"]) == 64
