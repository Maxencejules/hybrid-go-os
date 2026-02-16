"""M5 acceptance test: VirtIO block device detected on PCI bus."""


def test_virtio_blk_identify(qemu_serial):
    """Serial output must contain VirtIO block identification marker."""
    out = qemu_serial.stdout
    assert "BLK: found virtio-blk" in out, (
        f"Missing 'BLK: found virtio-blk'. Got:\n{out}"
    )
