"""M3 acceptance test: kernel kills faulting user task, system continues."""


def test_user_fault(qemu_serial):
    """Faulting user task killed; kernel continues running."""
    out = qemu_serial.stdout
    assert "USER: killed" in out, f"Missing 'USER: killed'. Got:\n{out}"
    assert "KERNEL: halt ok" in out, f"System crashed after user fault. Got:\n{out}"
