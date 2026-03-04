"""M9 acceptance: deterministic probe/init negative paths."""


def test_block_probe_missing_device(qemu_serial_blk_missing):
    """Missing block device must fail with deterministic probe marker."""
    out = qemu_serial_blk_missing.stdout
    assert "BLK: not found" in out, (
        f"Missing deterministic block probe-failure marker. Got:\n{out}"
    )


def test_net_probe_missing_device(qemu_serial_net_missing):
    """Missing NIC must fail with deterministic probe marker."""
    out = qemu_serial_net_missing.stdout
    assert "NET: not found" in out, (
        f"Missing deterministic net probe-failure marker. Got:\n{out}"
    )
