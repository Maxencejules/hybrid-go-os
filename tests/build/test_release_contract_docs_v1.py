"""M14 acceptance: release contract docs/tooling presence and content."""

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (_repo_root() / relpath).read_text(encoding="utf-8")


def test_release_contract_docs_and_tool_presence():
    root = _repo_root()
    required = [
        "docs/M14_EXECUTION_BACKLOG.md",
        "docs/build/default_lane_release_path_v1.md",
        "docs/build/release_policy_v1.md",
        "docs/build/versioning_scheme_v1.md",
        "docs/build/release_checklist_v1.md",
        "tools/build_release_bundle_v1.py",
        "tools/release_contract_v1.py",
    ]
    for rel in required:
        assert (root / rel).is_file(), f"missing M14 PR-1 artifact: {rel}"

    policy = _read("docs/build/release_policy_v1.md").lower()
    versioning = _read("docs/build/versioning_scheme_v1.md").lower()
    checklist = _read("docs/build/release_checklist_v1.md")

    assert "stable" in policy
    assert "beta" in policy
    assert "nightly" in policy
    assert "backport" in policy
    assert "major.minor.patch" in versioning
    assert "build_sequence" in versioning
    assert "out/release-bundle-v1.json" in checklist
    assert "out/release-contract-v1.json" in checklist
