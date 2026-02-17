"""M3 acceptance test: enter user mode and print via sys_debug_write."""


def test_enter_user_mode(qemu_serial_user_hello):
    """User program must print via sys_debug_write."""
    out = qemu_serial_user_hello.stdout
    assert "USER: hello" in out, f"Missing 'USER: hello'. Got:\n{out}"
