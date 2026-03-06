"""M28 acceptance: vulnerability response docs are present and complete."""

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (_repo_root() / relpath).read_text(encoding="utf-8").lower()


def test_vuln_response_docs_v1_present():
    root = _repo_root()
    required = [
        "docs/security/vulnerability_response_policy_v1.md",
        "docs/security/security_advisory_policy_v1.md",
        "tools/security_advisory_lint_v1.py",
        "tools/security_embargo_drill_v1.py",
    ]
    for rel in required:
        assert (root / rel).is_file(), f"missing M28 artifact: {rel}"

    response = _read("docs/security/vulnerability_response_policy_v1.md")
    advisory = _read("docs/security/security_advisory_policy_v1.md")
    assert "triage sla" in response
    assert "embargo" in response
    assert "advisory" in response
    assert "cve" in advisory
    assert "advisory_id" in advisory

