"""M5 acceptance test: VirtIO block read rejects invalid user pointer."""


def test_virtio_blk_badptr(qemu_serial_blk_badptr):
    """Serial output must confirm invalid pointer handling passed."""
    out = qemu_serial_blk_badptr.stdout
    assert "BLK: badptr ok" in out, (
        f"Missing 'BLK: badptr ok'. Got:\n{out}"
    )
