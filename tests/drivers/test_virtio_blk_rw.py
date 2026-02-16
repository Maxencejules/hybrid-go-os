"""M5 acceptance test: VirtIO block read/write round-trip."""


def test_virtio_blk_rw(qemu_serial):
    """Serial output must confirm block read/write self-test passed."""
    out = qemu_serial.stdout
    assert "BLK: rw ok" in out, (
        f"Missing 'BLK: rw ok'. Got:\n{out}"
    )
