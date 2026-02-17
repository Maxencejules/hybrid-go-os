"""M3 acceptance test: kernel kills faulting user task, system continues."""


def test_user_fault(qemu_serial_user_fault):
    """Faulting user task killed; kernel continues running."""
    out = qemu_serial_user_fault.stdout
    assert "USER: killed" in out, f"Missing 'USER: killed'. Got:\n{out}"
    assert "RUGO: halt ok" in out, (
        f"Kernel did not continue after user fault. Got:\n{out}"
    )
