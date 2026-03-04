"""M9 acceptance: hardware matrix v1 smoke checks."""

import pytest


@pytest.mark.parametrize(
    "fixture_name,tier,machine",
    [
        ("qemu_serial_blk_q35", "tier0", "q35"),
        ("qemu_serial_blk_i440fx", "tier1", "pc/i440fx"),
    ],
)
def test_storage_smoke_matrix(request, fixture_name, tier, machine):
    """Tiered profiles must pass deterministic block probe + rw smoke."""
    out = request.getfixturevalue(fixture_name).stdout
    assert "BLK: found virtio-blk" in out, (
        f"{tier} ({machine}) missing block probe marker. Got:\n{out}"
    )
    assert "BLK: rw ok" in out, (
        f"{tier} ({machine}) missing block rw marker. Got:\n{out}"
    )


@pytest.mark.parametrize(
    "fixture_name,tier,machine",
    [
        ("qemu_serial_net_q35", "tier0", "q35"),
        ("qemu_serial_net_i440fx", "tier1", "pc/i440fx"),
    ],
)
def test_network_smoke_matrix(request, fixture_name, tier, machine):
    """Tiered profiles must pass deterministic net probe + UDP echo smoke."""
    out = request.getfixturevalue(fixture_name).stdout
    assert "NET: virtio-net ready" in out, (
        f"{tier} ({machine}) missing net ready marker. Got:\n{out}"
    )
    assert "NET: udp echo" in out, (
        f"{tier} ({machine}) missing UDP echo marker. Got:\n{out}"
    )
