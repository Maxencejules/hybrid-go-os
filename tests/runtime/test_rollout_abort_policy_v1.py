"""M33 acceptance: rollout abort policy enforcement drill."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_rollout_abort_drill_v1 as drill  # noqa: E402


def test_rollout_abort_policy_v1(tmp_path: Path):
    out = tmp_path / "rollout-abort-drill-v1.json"
    rc = drill.main(["--out", str(out)])
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.rollout_abort_drill_report.v1"
    assert data["auto_halt"] is True
    assert data["rollback_triggered"] is True
    assert data["policy_enforced"] is True

