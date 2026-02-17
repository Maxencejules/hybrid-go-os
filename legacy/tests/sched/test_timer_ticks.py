"""M2 acceptance test: PIT timer fires and reaches tick 100."""


def test_timer_ticks(qemu_serial):
    """Serial output must contain the tick marker."""
    out = qemu_serial.stdout
    assert "TICK: 100" in out, f"Missing 'TICK: 100'. Got:\n{out}"
