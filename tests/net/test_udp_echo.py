"""M7: VirtIO net + UDP echo — Rugo lane acceptance test."""


def test_udp_echo(qemu_serial_net):
    """Guest must echo a UDP packet and print the marker."""
    assert "NET: udp echo" in qemu_serial_net.stdout
