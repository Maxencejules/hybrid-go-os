"""M13 acceptance: storage reliability gate and docs closure wiring."""

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (_repo_root() / relpath).read_text(encoding="utf-8")


def test_storage_reliability_gate_wiring():
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")

    assert "test-storage-reliability-v1" in makefile
    assert "Storage reliability v1 gate" in ci
    assert "M13" in milestones
    assert "M13" in status
    assert "Next execution backlog target: M14" in status
