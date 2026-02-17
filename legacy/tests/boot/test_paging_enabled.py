"""M1 acceptance test: paging is enabled."""


def test_paging_enabled(qemu_serial):
    """Serial output must confirm paging is on."""
    out = qemu_serial.stdout
    assert "MM: paging=on" in out, f"Missing 'MM: paging=on'. Got:\n{out}"
