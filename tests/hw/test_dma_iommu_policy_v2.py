"""M15 acceptance: DMA and IOMMU policy hardening checks for matrix v2."""

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (_repo_root() / relpath).read_text(encoding="utf-8")


def test_dma_rejects_non_sector_aligned_len_v2(qemu_serial_blk_badlen):
    """DMA path must deterministically reject non-sector-aligned lengths."""
    out = qemu_serial_blk_badlen.stdout
    assert "BLK: badlen ok" in out, (
        f"Missing v2 DMA bad-length rejection marker. Got:\n{out}"
    )


def test_dma_rejects_invalid_user_pointer_v2(qemu_serial_blk_badptr):
    """DMA path must deterministically reject invalid user pointers."""
    out = qemu_serial_blk_badptr.stdout
    assert "BLK: badptr ok" in out, (
        f"Missing v2 DMA bad-pointer rejection marker. Got:\n{out}"
    )


def test_dma_iommu_policy_contract_v2():
    """DMA strategy v2 must define fail-closed semantics and mode contract."""
    policy = _read("docs/hw/dma_iommu_strategy_v2.md")
    for token in [
        "fail-closed",
        "`off`",
        "`passthrough`",
        "`strict`",
        "software validation mandatory",
        "`tests/hw/test_dma_iommu_policy_v2.py`",
    ]:
        assert token in policy
