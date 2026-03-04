"""M13 acceptance: storage contract docs and gate wiring."""

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (_repo_root() / relpath).read_text(encoding="utf-8")


def test_storage_docs_tools_and_gate_wiring():
    root = _repo_root()
    required = [
        "docs/M13_EXECUTION_BACKLOG.md",
        "docs/storage/fs_v1.md",
        "docs/storage/durability_model_v1.md",
        "docs/storage/write_ordering_policy_v1.md",
        "docs/storage/recovery_playbook_v1.md",
        "docs/storage/fault_campaign_v1.md",
        "tools/storage_recover_v1.py",
        "tools/run_storage_fault_campaign_v1.py",
    ]
    for rel in required:
        assert (root / rel).is_file(), f"missing M13 artifact: {rel}"

    fs_v1 = _read("docs/storage/fs_v1.md")
    durability = _read("docs/storage/durability_model_v1.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")

    assert "Status: active release gate" in fs_v1
    assert "Durability classes" in fs_v1
    assert "`fsync`" in durability
    assert "test-storage-reliability-v1" in makefile
    assert "Storage reliability v1 gate" in ci
