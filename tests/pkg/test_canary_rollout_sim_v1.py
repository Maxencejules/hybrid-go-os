"""M33 acceptance: canary rollout simulation report schema."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_canary_rollout_sim_v1 as sim  # noqa: E402


def test_canary_rollout_sim_v1(tmp_path: Path):
    out = tmp_path / "canary-rollout-sim-v1.json"
    rc = sim.main(["--seed", "20260305", "--out", str(out)])
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.canary_rollout_report.v1"
    assert len(data["stages"]) == 3
    assert "halted" in data

