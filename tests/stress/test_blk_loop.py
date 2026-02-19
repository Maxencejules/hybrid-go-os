"""Stress VirtIO block acceptance: deterministic write/read verification loop."""


def test_blk_loop(qemu_serial_stress_blk):
    """Kernel must survive repetitive block I/O and print success marker."""
    out = qemu_serial_stress_blk.stdout
    assert "STRESS: blk ok" in out, (
        f"Missing 'STRESS: blk ok'. Got:\n{out}"
    )
