"""M15 acceptance: hardware matrix v2 tier checks and contract references."""

from pathlib import Path

import pytest


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (_repo_root() / relpath).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "fixture_name,tier,machine",
    [
        ("qemu_serial_blk_q35", "tier0", "q35"),
        ("qemu_serial_blk_i440fx", "tier1", "pc/i440fx"),
    ],
)
def test_storage_smoke_matrix_v2(request, fixture_name, tier, machine):
    """Tier 0 and Tier 1 must keep deterministic storage probe/rw markers."""
    out = request.getfixturevalue(fixture_name).stdout
    assert "BLK: found virtio-blk" in out, (
        f"{tier} ({machine}) missing storage probe marker. Got:\n{out}"
    )
    assert "BLK: rw ok" in out, (
        f"{tier} ({machine}) missing storage rw marker. Got:\n{out}"
    )


@pytest.mark.parametrize(
    "fixture_name,tier,machine",
    [
        ("qemu_serial_net_q35", "tier0", "q35"),
        ("qemu_serial_net_i440fx", "tier1", "pc/i440fx"),
    ],
)
def test_network_smoke_matrix_v2(request, fixture_name, tier, machine):
    """Tier 0 and Tier 1 must keep deterministic network probe/runtime markers."""
    out = request.getfixturevalue(fixture_name).stdout
    assert "NET: virtio-net ready" in out, (
        f"{tier} ({machine}) missing network ready marker. Got:\n{out}"
    )
    assert "NET: udp echo" in out, (
        f"{tier} ({machine}) missing UDP echo marker. Got:\n{out}"
    )


def test_matrix_v2_contract_and_artifact_schema():
    """Support matrix v2 must define tier criteria and evidence schema."""
    matrix = _read("docs/hw/support_matrix_v2.md")
    profile = _read("docs/hw/device_profile_contract_v2.md")

    for token in [
        "Tier 0",
        "Tier 1",
        "Tier 2",
        "Schema identifier: `rugo.hw_matrix_evidence.v2`",
        "Local gate: `make test-hw-matrix-v2`",
        "Hardware claims are bounded to matrix evidence only.",
    ]:
        assert token in matrix

    for token in [
        "`probe_missing`",
        "`init_ready`",
        "`runtime_ok`",
        "`dma_reject_badlen`",
        "`dma_reject_badptr`",
    ]:
        assert token in profile
