"""Roadmap/docs: C5 closure is wired to runtime evidence and gates."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_core_scoreboards_mark_c5_done():
    framework = _read("docs/roadmap/MILESTONE_FRAMEWORK.md")
    roadmap = _read("docs/roadmap/README.md")
    readme = _read("README.md")

    assert "| `C5` Reliable and Isolated Service OS | done |" in framework
    assert "`C3` done; `C4` done; `C5` done." in framework
    assert "`C3` done; `C4` done; `C5` done." in roadmap
    assert "`C3` done; `C4` done; `C5` done." in readme


def test_core_runtime_closure_doc_marks_c5_rows_runtime_backed():
    doc = _read("docs/roadmap/implementation_closure/core_runtime.md")

    for row in [
        "| `M22 Kernel Reliability + Soak v1` | `Closed` | `Runtime-backed` |",
        "| `M42 Isolation + Namespace Baseline v1` | `Closed` | `Runtime-backed` |",
    ]:
        assert row in doc

    assert "`M10`, `M12`, `M13`, `M16`, `M18`, `M19`, `M22`, `M25`, and `M42`" in doc


def test_c5_gate_and_contract_docs_are_wired():
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    syscall = _read("docs/abi/syscall_v1.md")
    reliability = _read("docs/runtime/kernel_reliability_model_v1.md")
    namespace = _read("docs/abi/namespace_cgroup_contract_v1.md")
    policy = _read("docs/runtime/resource_control_policy_v1.md")

    assert "test-reliable-isolated-runtime-c5: image-go" in makefile
    assert "tests/runtime/test_reliable_isolated_runtime_c5.py" in makefile
    assert "tests/runtime/test_c5_status_docs.py" in makefile
    assert "pytest-reliable-isolated-runtime-c5.xml" in makefile

    assert "Reliable isolated runtime C5 gate" in ci
    assert "make test-reliable-isolated-runtime-c5" in ci
    assert "reliable-isolated-runtime-c5-artifacts" in ci
    assert "out/pytest-reliable-isolated-runtime-c5.xml" in ci

    assert "| 41 | `sys_isolation_config` |" in syscall
    assert "make test-reliable-isolated-runtime-c5" in reliability
    assert "make test-reliable-isolated-runtime-c5" in namespace
    assert "make test-reliable-isolated-runtime-c5" in policy
