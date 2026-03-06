"""M33 aggregate gate: fleet rollout safety checks."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_canary_rollout_sim_v1 as canary  # noqa: E402
import run_rollout_abort_drill_v1 as abort  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_fleet_rollout_safety_gate_v1(tmp_path: Path):
    required = [
        "docs/pkg/staged_rollout_policy_v1.md",
        "docs/runtime/canary_slo_policy_v1.md",
        "tools/run_canary_rollout_sim_v1.py",
        "tools/run_rollout_abort_drill_v1.py",
        "tests/pkg/test_canary_rollout_sim_v1.py",
        "tests/runtime/test_rollout_abort_policy_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing gate artifact: {rel}"

    roadmap = _read("docs/M21_M34_MATURITY_PARITY_ROADMAP.md")
    assert "test-fleet-rollout-safety-v1" in roadmap

    canary_out = tmp_path / "canary-rollout-sim-v1.json"
    abort_out = tmp_path / "rollout-abort-drill-v1.json"
    assert canary.main(["--out", str(canary_out)]) == 0
    assert abort.main(["--out", str(abort_out)]) == 0

    canary_data = json.loads(canary_out.read_text(encoding="utf-8"))
    abort_data = json.loads(abort_out.read_text(encoding="utf-8"))
    assert canary_data["schema"] == "rugo.canary_rollout_report.v1"
    assert abort_data["policy_enforced"] is True

