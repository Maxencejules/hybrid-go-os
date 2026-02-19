"""Stress syscall acceptance: ring3 spam of valid+invalid syscall mix."""


def test_syscall_spam(qemu_serial_stress_syscall):
    """Kernel must survive syscall spam and print success marker."""
    out = qemu_serial_stress_syscall.stdout
    assert "STRESS: syscall ok" in out, (
        f"Missing 'STRESS: syscall ok'. Got:\n{out}"
    )
