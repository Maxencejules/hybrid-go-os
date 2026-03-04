"""M11 acceptance: runtime ABI-window and coverage policy checks."""

from pathlib import Path


RUNTIME_SYSCALLS = [
    "sys_debug_write",
    "sys_thread_spawn",
    "sys_thread_exit",
    "sys_yield",
    "sys_vm_map",
    "sys_vm_unmap",
    "sys_time_now",
    "sys_open",
    "sys_read",
    "sys_write",
    "sys_close",
    "sys_poll",
]


def _read(relpath: str) -> str:
    root = Path(__file__).resolve().parents[2]
    return (root / relpath).read_text(encoding="utf-8")


def test_runtime_abi_window_and_syscall_alignment():
    policy = _read("docs/runtime/abi_stability_policy_v1.md")
    matrix = _read("docs/runtime/syscall_coverage_matrix_v1.md")
    syscall_v0 = _read("docs/abi/syscall_v0.md")
    syscall_v1 = _read("docs/abi/syscall_v1.md")

    assert "Stability window:" in policy
    assert "2026-03-04" in policy
    assert "Deprecation and breakage process" in policy

    for symbol in RUNTIME_SYSCALLS:
        quoted = f"`{symbol}`"
        assert quoted in matrix, f"{symbol} missing from runtime matrix"
        assert quoted in policy, f"{symbol} missing from ABI policy"
        assert (
            quoted in syscall_v0 or quoted in syscall_v1
        ), f"{symbol} missing from syscall ABI docs"


def test_runtime_matrix_has_owned_rows_and_no_placeholders():
    matrix = _read("docs/runtime/syscall_coverage_matrix_v1.md")
    lowered = matrix.lower()
    assert "owner" in lowered
    assert "todo" not in lowered
    assert "tbd" not in lowered
    assert "unassigned" not in lowered
