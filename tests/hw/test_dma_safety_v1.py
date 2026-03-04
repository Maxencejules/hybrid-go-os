"""M9 acceptance: DMA boundary + invalid-mapping rejection checks."""


def test_dma_rejects_non_sector_aligned_len(qemu_serial_blk_badlen):
    """Block DMA path must reject non-sector-aligned lengths."""
    out = qemu_serial_blk_badlen.stdout
    assert "BLK: badlen ok" in out, (
        f"Missing DMA bad-length rejection marker. Got:\n{out}"
    )


def test_dma_rejects_invalid_user_pointer(qemu_serial_blk_badptr):
    """Block DMA path must reject unmapped user pointers deterministically."""
    out = qemu_serial_blk_badptr.stdout
    assert "BLK: badptr ok" in out, (
        f"Missing DMA bad-pointer rejection marker. Got:\n{out}"
    )
