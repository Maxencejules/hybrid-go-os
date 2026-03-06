"""M28 acceptance: advisory schema lint passes for baseline advisory."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import security_advisory_lint_v1 as lint_tool  # noqa: E402


def test_advisory_schema_v1(tmp_path: Path):
    out = tmp_path / "security-advisory-lint-v1.json"
    rc = lint_tool.main(["--out", str(out)])
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.security_advisory_lint_report.v1"
    assert data["total_errors"] == 0
    assert data["valid"] is True

