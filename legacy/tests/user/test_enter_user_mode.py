"""M3 acceptance test: enter user mode and print via sys_debug_write."""


def test_enter_user_mode(qemu_serial):
    """User program must print via sys_debug_write."""
    out = qemu_serial.stdout
    assert "USER: hello" in out, f"Missing 'USER: hello'. Got:\n{out}"
