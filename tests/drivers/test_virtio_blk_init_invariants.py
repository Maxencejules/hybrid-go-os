"""M5 acceptance test: VirtIO block init queue-size invariants check."""


def test_virtio_blk_init_invariants(qemu_serial_blk_invariants):
    """Serial output must confirm init invariants passed."""
    out = qemu_serial_blk_invariants.stdout
    assert "BLK: invariants ok" in out, (
        f"Missing 'BLK: invariants ok'. Got:\n{out}"
    )
