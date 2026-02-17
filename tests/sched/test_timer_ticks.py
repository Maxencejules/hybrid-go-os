"""M2 acceptance test: PIT timer fires and tick counter reaches 100."""


def test_timer_ticks(qemu_serial_sched):
    """Serial output must contain 'TICK: 100' proving PIT + PIC + IRQ0 work."""
    out = qemu_serial_sched.stdout
    assert "TICK: 100" in out, f"Missing 'TICK: 100'. Got:\n{out}"
