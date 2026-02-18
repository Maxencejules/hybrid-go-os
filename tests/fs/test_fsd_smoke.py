"""M6 acceptance test: FSD mounts SimpleFS."""


def test_fsd_smoke(qemu_serial_fs):
    """Serial output must contain FSD mount success marker."""
    out = qemu_serial_fs.stdout
    assert "FSD: mount ok" in out, (
        f"Missing 'FSD: mount ok'. Got:\n{out}"
    )
