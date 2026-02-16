"""G0 acceptance test: Go kernel entry executes."""


def test_go_entry(qemu_serial):
    """Serial output must contain Go entry marker and M0 markers."""
    out = qemu_serial.stdout
    assert "GO: kmain ok" in out, f"Missing 'GO: kmain ok'. Got:\n{out}"
    assert "KERNEL: boot ok" in out, f"Missing 'KERNEL: boot ok'. Got:\n{out}"
    assert "KERNEL: halt ok" in out, f"Missing 'KERNEL: halt ok'. Got:\n{out}"
