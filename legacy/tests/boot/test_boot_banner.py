"""M0 acceptance test: boot banner and clean halt."""


def test_boot_banner(qemu_serial):
    """Serial output must contain the required boot markers."""
    out = qemu_serial.stdout
    assert "KERNEL: boot ok" in out, f"Missing 'KERNEL: boot ok'. Got:\n{out}"
    assert "KERNEL: halt ok" in out, f"Missing 'KERNEL: halt ok'. Got:\n{out}"
