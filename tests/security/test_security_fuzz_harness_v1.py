"""M10 acceptance: security fuzz harness gate."""

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2] / "tools"))
import run_security_fuzz_v1 as fuzz  # noqa: E402


def test_security_fuzz_harness_report(tmp_path: Path):
    out = tmp_path / "security-fuzz-report.json"
    rc = fuzz.main(
        [
            "--seed",
            "20260304",
            "--iterations",
            "400",
            "--cases",
            "3",
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    assert out.is_file()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.security_fuzz_report.v1"
    assert data["total_violations"] == 0
    assert data["crash_sla_hours"] == 24
