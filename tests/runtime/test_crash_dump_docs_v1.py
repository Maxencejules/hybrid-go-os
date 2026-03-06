"""M29 acceptance: crash dump and triage docs are present."""

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (_repo_root() / relpath).read_text(encoding="utf-8").lower()


def test_crash_dump_docs_v1_present():
    root = _repo_root()
    required = [
        "docs/runtime/crash_dump_contract_v1.md",
        "docs/runtime/postmortem_triage_playbook_v1.md",
        "tools/collect_crash_dump_v1.py",
        "tools/symbolize_crash_dump_v1.py",
    ]
    for rel in required:
        assert (root / rel).is_file(), f"missing M29 artifact: {rel}"

    contract = _read("docs/runtime/crash_dump_contract_v1.md")
    playbook = _read("docs/runtime/postmortem_triage_playbook_v1.md")
    assert "panic" in contract
    assert "register" in contract
    assert "symbolize" in playbook
    assert "triage" in playbook

