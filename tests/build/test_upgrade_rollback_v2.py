"""M20 acceptance: upgrade and rollback drill v2 behavior."""

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_upgrade_recovery_drill_v2 as drill_tool  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_update_and_rollback_docs_present_with_contract_tokens():
    required = [
        "docs/pkg/update_protocol_v2.md",
        "docs/pkg/rollback_policy_v2.md",
        "tools/run_upgrade_recovery_drill_v2.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M20 PR-2 artifact: {rel}"

    update_protocol = _read("docs/pkg/update_protocol_v2.md")
    rollback_policy = _read("docs/pkg/rollback_policy_v2.md")

    for token in [
        "Schema ID: `rugo.update_metadata.v2`",
        "`rollback_floor_sequence`",
        "`recovery_plan_id`",
    ]:
        assert token in update_protocol

    for token in [
        "schema: `rugo.upgrade_recovery_drill.v2`",
        "`upgrade_apply`",
        "`rollback_activate`",
        "`test-release-ops-v2`",
    ]:
        assert token in rollback_policy


def test_upgrade_recovery_drill_v2_schema(tmp_path: Path):
    out = tmp_path / "upgrade-recovery-v2.json"
    rc = drill_tool.main(["--seed", "20260309", "--out", str(out)])
    assert rc == 0
    assert out.is_file()

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.upgrade_recovery_drill.v2"
    assert data["seed"] == 20260309
    assert data["failed_cases"] == 0
    assert data["total_failures"] == 0
    assert data["meets_target"] is True
    assert data["state_transition"]["final_state"]["active_slot"] == "A"
    assert [stage["name"] for stage in data["stages"]] == [
        "upgrade_apply",
        "post_upgrade_health_check",
        "rollback_activate",
        "recovery_bootstrap",
    ]
