"""M11 acceptance: runtime/toolchain docs and gate wiring."""

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (_repo_root() / relpath).read_text(encoding="utf-8")


def test_runtime_docs_and_gate_wiring():
    root = _repo_root()
    required = [
        "docs/M11_EXECUTION_BACKLOG.md",
        "docs/runtime/port_contract_v1.md",
        "docs/runtime/syscall_coverage_matrix_v1.md",
        "docs/runtime/abi_stability_policy_v1.md",
        "docs/runtime/toolchain_bootstrap_v1.md",
        "docs/runtime/maintainers_v1.md",
        "tools/bootstrap_go_port_v1.sh",
        "tools/runtime_toolchain_contract_v1.py",
    ]
    for rel in required:
        assert (root / rel).is_file(), f"missing M11 artifact: {rel}"

    port_doc = _read("docs/runtime/port_contract_v1.md")
    matrix_doc = _read("docs/runtime/syscall_coverage_matrix_v1.md")
    bootstrap_doc = _read("docs/runtime/toolchain_bootstrap_v1.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")

    assert "Target GOOS: `rugo`" in port_doc
    assert "Target GOARCH: `amd64`" in port_doc
    assert "`sys_thread_spawn`" in matrix_doc
    assert "`sys_poll`" in matrix_doc
    assert "make test-runtime-maturity" in bootstrap_doc
    assert "test-runtime-maturity" in makefile
    assert "Runtime + toolchain maturity v1 gate" in ci
