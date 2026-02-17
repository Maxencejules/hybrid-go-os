"""M0 acceptance test: panic path prints deterministic marker."""


def test_panic_path(qemu_serial_panic):
    """Panic handler must print a deterministic panic code marker."""
    out = qemu_serial_panic.stdout
    assert "RUGO: panic code=" in out, f"Missing 'RUGO: panic code='. Got:\n{out}"
