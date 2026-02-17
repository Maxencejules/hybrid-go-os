"""M1 acceptance test: paging is enabled at boot."""


def test_paging_enabled(qemu_serial):
    """CR0.PG must be set; serial output confirms MM: paging=on."""
    out = qemu_serial.stdout
    assert "MM: paging=on" in out, f"Missing 'MM: paging=on'. Got:\n{out}"
