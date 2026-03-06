"""M17 aggregate gate: compatibility profile v2 contract and gate wiring."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_compat_v2_gate_wiring_and_artifacts():
    required = [
        "docs/M17_EXECUTION_BACKLOG.md",
        "docs/abi/syscall_v2.md",
        "docs/abi/compat_profile_v2.md",
        "docs/abi/elf_loader_contract_v2.md",
        "docs/runtime/syscall_coverage_matrix_v2.md",
        "tests/compat/v2_model.py",
        "tests/compat/test_abi_profile_v2_docs.py",
        "tests/compat/test_elf_loader_dynamic_v2.py",
        "tests/compat/test_posix_profile_v2.py",
        "tests/compat/test_external_apps_tier_v2.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M17 artifact: {rel}"

    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M17_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")

    assert "test-compat-v2" in makefile
    for test_name in [
        "tests/compat/test_abi_profile_v2_docs.py",
        "tests/compat/test_elf_loader_dynamic_v2.py",
        "tests/compat/test_posix_profile_v2.py",
        "tests/compat/test_external_apps_tier_v2.py",
        "tests/compat/test_compat_gate_v2.py",
    ]:
        assert test_name in makefile
    assert "pytest-compat-v2.xml" in makefile

    assert "Compatibility profile v2 gate" in ci
    assert "make test-compat-v2" in ci
    assert "compat-v2-junit" in ci

    assert "Status: done" in backlog
    assert "M17" in milestones
    assert "M17" in status

