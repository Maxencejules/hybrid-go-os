"""M6 acceptance test: FSD mounts SimpleFS."""


def test_fsd_smoke(qemu_serial):
    """Serial output must contain FSD mount success marker."""
    out = qemu_serial.stdout
    assert "FSD: mount ok" in out, (
        f"Missing 'FSD: mount ok'. Got:\n{out}"
    )
