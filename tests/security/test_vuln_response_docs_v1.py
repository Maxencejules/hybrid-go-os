"""M28 PR-1: vulnerability-response and advisory policy docs v1 contracts."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_vuln_response_docs_v1_artifacts_exist():
    required = [
        "docs/M28_EXECUTION_BACKLOG.md",
        "docs/security/vulnerability_response_policy_v1.md",
        "docs/security/security_advisory_policy_v1.md",
        "tools/security_advisory_lint_v1.py",
        "tools/security_embargo_drill_v1.py",
        "tests/security/test_vuln_response_docs_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M28 artifact: {rel}"


def test_vuln_response_docs_declare_required_contract_tokens():
    response = _read("docs/security/vulnerability_response_policy_v1.md")
    advisory = _read("docs/security/security_advisory_policy_v1.md")

    for token in [
        "Policy ID: `rugo.vulnerability_response_policy.v1`",
        "Embargo drill schema: `rugo.security_embargo_drill_report.v1`",
        "Advisory lint schema: `rugo.security_advisory_lint_report.v1`",
        "Initial triage SLA: 24h.",
        "Severity assignment SLA: 72h.",
        "Sub-gate: `make test-vuln-response-v1`",
        "Parent gate: `make test-security-hardening-v3`",
    ]:
        assert token in response

    for token in [
        "Policy ID: `rugo.security_advisory_policy.v1`",
        "Lint report schema: `rugo.security_advisory_lint_report.v1`",
        "Linked response policy: `rugo.vulnerability_response_policy.v1`",
        "advisory_id",
        "severity",
        "cve_ids",
        "Sub-gate: `make test-vuln-response-v1`",
    ]:
        assert token in advisory


def test_m28_roadmap_anchor_declares_vuln_response_sub_gate():
    roadmap = _read("docs/M21_M34_MATURITY_PARITY_ROADMAP.md")
    assert "test-vuln-response-v1" in roadmap
