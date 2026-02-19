"""M5 acceptance test: VirtIO block read rejects non-sector-aligned length."""


def test_virtio_blk_badlen(qemu_serial_blk_badlen):
    """Serial output must confirm invalid length handling passed."""
    out = qemu_serial_blk_badlen.stdout
    assert "BLK: badlen ok" in out, (
        f"Missing 'BLK: badlen ok'. Got:\n{out}"
    )
