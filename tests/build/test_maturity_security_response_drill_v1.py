"""M34 acceptance: maturity bundle includes security response drill evidence."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import security_advisory_lint_v1 as advisory  # noqa: E402
import security_embargo_drill_v1 as embargo  # noqa: E402


def test_maturity_security_response_drill_v1(tmp_path: Path):
    advisory_out = tmp_path / "security-advisory-lint-v1.json"
    embargo_out = tmp_path / "security-embargo-drill-v1.json"
    assert advisory.main(["--out", str(advisory_out)]) == 0
    assert embargo.main(["--out", str(embargo_out)]) == 0
    advisory_data = json.loads(advisory_out.read_text(encoding="utf-8"))
    embargo_data = json.loads(embargo_out.read_text(encoding="utf-8"))
    assert advisory_data["valid"] is True
    assert embargo_data["meets_sla"] is True

