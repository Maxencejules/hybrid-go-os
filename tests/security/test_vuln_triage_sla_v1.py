"""M28 acceptance: triage SLA drill remains within policy window."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import security_embargo_drill_v1 as drill  # noqa: E402


def test_vuln_triage_sla_v1(tmp_path: Path):
    out = tmp_path / "security-embargo-drill-v1.json"
    rc = drill.main(["--out", str(out)])
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.security_embargo_drill_report.v1"
    assert data["triage_elapsed_hours"] <= data["triage_sla_hours"]
    assert data["meets_sla"] is True

