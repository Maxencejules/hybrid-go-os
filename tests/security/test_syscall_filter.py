"""M10 acceptance: syscall/profile sandbox enforcement."""


def test_security_syscall_filter(qemu_serial_sec_filter):
    """Restricted profile must block forbidden syscalls and paths."""
    out = qemu_serial_sec_filter.stdout
    assert "SEC: filter ok" in out, (
        f"Missing 'SEC: filter ok'. Got:\n{out}"
    )
