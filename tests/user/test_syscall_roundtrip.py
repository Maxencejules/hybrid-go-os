"""M3 acceptance test: syscall roundtrip (debug_write + time_now)."""


def test_syscall_roundtrip(qemu_serial_syscall):
    """User program must successfully call multiple syscalls."""
    out = qemu_serial_syscall.stdout
    assert "SYSCALL: ok" in out, f"Missing 'SYSCALL: ok'. Got:\n{out}"
