"""M6 acceptance test: FSD rejects a bad superblock magic."""


def test_fsd_bad_magic(qemu_serial_fs_badmagic):
    """Serial output must contain the bad-magic marker."""
    out = qemu_serial_fs_badmagic.stdout
    assert "FSD: bad magic" in out, (
        f"Missing 'FSD: bad magic'. Got:\n{out}"
    )
