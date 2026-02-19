"""M3 acceptance test: minimal cooperative sys_yield."""


def test_yield(qemu_serial_yield):
    """User program must call sys_yield and print pass marker."""
    out = qemu_serial_yield.stdout
    assert "YIELD: ok" in out, f"Missing 'YIELD: ok'. Got:\n{out}"
