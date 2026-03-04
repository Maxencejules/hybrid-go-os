"""M12 acceptance: IPv4/UDP contract behavior."""

from pathlib import Path

import pytest


def _profile_text() -> str:
    path = Path(__file__).resolve().parents[2] / "docs" / "net" / "ipv4_udp_profile_v1.md"
    return path.read_text(encoding="utf-8")


def test_ipv4_udp_profile_doc_markers_and_abi_boundary():
    text = _profile_text()
    assert "`NET: virtio-net ready`" in text
    assert "`NET: udp echo`" in text
    assert "`NET: not found`" in text
    assert "`sys_net_send`" in text
    assert "`sys_net_recv`" in text


@pytest.mark.parametrize(
    "fixture_name,tier,machine",
    [
        ("qemu_serial_net_q35", "tier0", "q35"),
        ("qemu_serial_net_i440fx", "tier1", "pc/i440fx"),
    ],
)
def test_ipv4_udp_positive_matrix(request, fixture_name, tier, machine):
    out = request.getfixturevalue(fixture_name).stdout
    assert "NET: virtio-net ready" in out, (
        f"{tier} ({machine}) missing net-ready marker. Got:\n{out}"
    )
    assert "NET: udp echo" in out, (
        f"{tier} ({machine}) missing udp-echo marker. Got:\n{out}"
    )


def test_ipv4_udp_missing_nic_negative_path(qemu_serial_net_missing):
    out = qemu_serial_net_missing.stdout
    assert "NET: not found" in out, (
        f"Missing deterministic no-NIC marker. Got:\n{out}"
    )
