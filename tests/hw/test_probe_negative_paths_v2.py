"""M15 acceptance: deterministic probe/init negative paths for matrix v2."""

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (_repo_root() / relpath).read_text(encoding="utf-8")


def test_block_probe_missing_device_v2(qemu_serial_blk_missing):
    """Missing block device must keep deterministic v2 failure marker."""
    out = qemu_serial_blk_missing.stdout
    assert "BLK: not found" in out, (
        f"Missing deterministic block probe marker for v2. Got:\n{out}"
    )


def test_net_probe_missing_device_v2(qemu_serial_net_missing):
    """Missing NIC must keep deterministic v2 failure marker."""
    out = qemu_serial_net_missing.stdout
    assert "NET: not found" in out, (
        f"Missing deterministic net probe marker for v2. Got:\n{out}"
    )


def test_negative_path_contract_states_present():
    """Device contract must keep explicit negative-path state semantics."""
    profile = _read("docs/hw/device_profile_contract_v2.md")
    for token in [
        "Deterministic lifecycle states",
        "`probe_missing`",
        "`BLK: not found`",
        "`NET: not found`",
    ]:
        assert token in profile
