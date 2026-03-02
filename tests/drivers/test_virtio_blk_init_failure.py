"""M5 acceptance test: VirtIO block init failure path emits deterministic marker."""


def test_virtio_blk_init_failure(qemu_serial_blk_init_fail):
    """Serial output must confirm the block driver init-failure path was hit."""
    out = qemu_serial_blk_init_fail.stdout
    assert "BLK: init failed" in out, (
        f"Missing 'BLK: init failed'. Got:\n{out}"
    )
