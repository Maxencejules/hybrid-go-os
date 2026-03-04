"""M14 acceptance: update attack campaign artifact generation."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_update_attack_suite_v1 as suite  # noqa: E402


def test_update_attack_suite_report(tmp_path: Path):
    out = tmp_path / "update-attack-suite-v1.json"
    rc = suite.main(
        [
            "--seed",
            "20260304",
            "--max-failures",
            "0",
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    assert out.is_file()

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.update_attack_suite_report.v1"
    assert data["total_cases"] >= 5
    assert data["total_failures"] == 0
    assert data["meets_target"] is True
