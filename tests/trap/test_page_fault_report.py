"""M1 acceptance test: page fault handler reports address and error code."""


def test_page_fault_report(qemu_serial):
    """Serial output must contain the PF marker with address and error code."""
    out = qemu_serial.stdout
    assert "PF: addr=0x" in out, f"Missing 'PF: addr=0x'. Got:\n{out}"
    assert "err=0x" in out, f"Missing 'err=0x'. Got:\n{out}"
