"""M12 acceptance: network soak/fault-injection artifact generation."""

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2] / "tools"))
import run_net_soak_v1 as soak  # noqa: E402


def test_net_soak_report(tmp_path: Path):
    out = tmp_path / "net-soak-v1.json"
    rc = soak.main(
        [
            "--seed",
            "20260304",
            "--iterations",
            "600",
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    assert out.is_file()

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.net_soak_report.v1"
    assert data["total_failures"] == 0
    assert data["meets_target"] is True
    assert data["iterations"] == 600
