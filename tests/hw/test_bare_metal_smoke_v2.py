"""M15 acceptance: bare-metal lane runbook and smoke criteria for matrix v2."""

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (_repo_root() / relpath).read_text(encoding="utf-8")


def test_tier0_smoke_markers_for_bare_metal_lane_v2(
    qemu_serial_blk_q35, qemu_serial_net_q35
):
    """Tier 0 baseline markers must remain stable for runbook smoke usage."""
    blk_out = qemu_serial_blk_q35.stdout
    net_out = qemu_serial_net_q35.stdout

    assert "RUGO: boot ok" in blk_out
    assert "BLK: found virtio-blk" in blk_out
    assert "BLK: rw ok" in blk_out

    assert "RUGO: boot ok" in net_out
    assert "NET: virtio-net ready" in net_out
    assert "NET: udp echo" in net_out


def test_bare_metal_runbook_v2_has_required_evidence_bundle():
    """Runbook must pin required evidence artifacts and promotion thresholds."""
    runbook = _read("docs/hw/bare_metal_bringup_v2.md")
    for token in [
        "Required evidence bundle",
        "`out/pytest-hw-matrix-v2.xml`",
        "`hw-matrix-v2-junit`",
        "minimum 5 consecutive runs",
        "make test-hw-matrix-v2",
    ]:
        assert token in runbook
