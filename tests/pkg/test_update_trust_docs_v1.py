"""M26 acceptance: update trust docs and tools are present."""

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (_repo_root() / relpath).read_text(encoding="utf-8").lower()


def test_update_trust_docs_v1_present():
    root = _repo_root()
    required = [
        "docs/pkg/update_trust_model_v1.md",
        "docs/security/update_key_rotation_policy_v1.md",
        "tools/check_update_trust_v1.py",
        "tools/run_update_key_rotation_drill_v1.py",
    ]
    for rel in required:
        assert (root / rel).is_file(), f"missing M26 artifact: {rel}"

    trust = _read("docs/pkg/update_trust_model_v1.md")
    rotation = _read("docs/security/update_key_rotation_policy_v1.md")
    assert "rollback" in trust
    assert "freeze" in trust
    assert "mix-and-match" in trust
    assert "rotation" in rotation
    assert "revok" in rotation

