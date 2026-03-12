"""Roadmap docs: C4 remains aligned after the C5 closure lands."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_core_scoreboards_mark_c4_done():
    framework = _read("docs/roadmap/MILESTONE_FRAMEWORK.md")
    roadmap = _read("docs/roadmap/README.md")
    readme = _read("README.md")

    assert "| `C4` Durable and Connected Runtime | done |" in framework
    assert "`C3` done; `C4` done; `C5` done." in framework
    assert "`C3` done; `C4` done; `C5` done." in roadmap
    assert "`C3` done; `C4` done; `C5` done." in readme


def test_core_runtime_closure_doc_marks_c4_rows_runtime_backed():
    doc = _read("docs/roadmap/implementation_closure/core_runtime.md")

    for row in [
        "| `M12 Network stack v1` | `Closed` | `Runtime-backed` |",
        "| `M13 Storage reliability v1` | `Closed` | `Runtime-backed` |",
        "| `M18 Storage reliability v2` | `Closed` | `Runtime-backed` |",
        "| `M19 Network stack v2` | `Closed` | `Runtime-backed` |",
    ]:
        assert row in doc

    assert "`M10`, `M12`, `M13`, `M16`, `M18`, `M19`" in doc


def test_connected_runtime_gate_and_abi_docs_are_wired():
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    syscall = _read("docs/abi/syscall_v1.md")
    net_contract = _read("docs/net/network_stack_contract_v2.md")
    storage_playbook = _read("docs/storage/recovery_playbook_v2.md")

    assert "test-connected-runtime-c4: image-go" in makefile
    assert "tests/runtime/test_connected_runtime_c4.py" in makefile
    assert "tests/runtime/test_c4_status_docs.py" in makefile
    assert "pytest-connected-runtime-c4.xml" in makefile

    assert "Connected runtime C4 gate" in ci
    assert "make test-connected-runtime-c4" in ci
    assert "connected-runtime-c4-artifacts" in ci
    assert "out/pytest-connected-runtime-c4.xml" in ci

    for entry in [
        "| 30 | `sys_fsync` |",
        "| 31 | `sys_socket_open` |",
        "| 39 | `sys_net_if_config` |",
        "| 40 | `sys_net_route_add` |",
    ]:
        assert entry in syscall

    assert "make test-connected-runtime-c4" in net_contract
    assert "make test-connected-runtime-c4" in storage_playbook
