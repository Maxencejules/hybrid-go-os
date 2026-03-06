"""M28 aggregate gate: vulnerability response and advisory workflow checks."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import security_advisory_lint_v1 as lint_tool  # noqa: E402
import security_embargo_drill_v1 as embargo  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_vuln_response_gate_v1(tmp_path: Path):
    required = [
        "docs/security/vulnerability_response_policy_v1.md",
        "docs/security/security_advisory_policy_v1.md",
        "tools/security_advisory_lint_v1.py",
        "tools/security_embargo_drill_v1.py",
        "tests/security/test_vuln_triage_sla_v1.py",
        "tests/security/test_embargo_workflow_v1.py",
        "tests/security/test_advisory_schema_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing gate artifact: {rel}"

    roadmap = _read("docs/M21_M34_MATURITY_PARITY_ROADMAP.md")
    assert "test-vuln-response-v1" in roadmap

    lint_out = tmp_path / "security-advisory-lint-v1.json"
    embargo_out = tmp_path / "security-embargo-drill-v1.json"
    assert lint_tool.main(["--out", str(lint_out)]) == 0
    assert embargo.main(["--out", str(embargo_out)]) == 0

    lint_data = json.loads(lint_out.read_text(encoding="utf-8"))
    embargo_data = json.loads(embargo_out.read_text(encoding="utf-8"))
    assert lint_data["total_errors"] == 0
    assert embargo_data["meets_sla"] is True

