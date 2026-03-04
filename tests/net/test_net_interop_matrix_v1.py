"""M12 acceptance: interop matrix artifact generation."""

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2] / "tools"))
import run_net_interop_matrix_v1 as interop  # noqa: E402


def test_net_interop_matrix_report(tmp_path: Path):
    out = tmp_path / "net-interop-v1.json"
    rc = interop.main(["--out", str(out), "--target-pass-rate", "1.0"])
    assert rc == 0
    assert out.is_file()

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.net_interop_matrix.v1"
    assert data["total_cases"] >= 4
    assert data["passed_cases"] == data["total_cases"]
    assert data["pass_rate"] == 1.0
    assert data["meets_target"] is True
