"""M7: VirtIO net + UDP echo — Rugo lane acceptance test."""


def test_udp_echo(qemu_serial_net):
    """Guest must echo a UDP packet and print deterministic markers."""
    out = qemu_serial_net.stdout
    assert "NET: virtio-net ready" in out, f"Missing net-ready marker. Got:\n{out}"
    assert "NET: udp echo" in out, f"Missing udp-echo marker. Got:\n{out}"
    assert "NET: timeout" not in out, f"Unexpected net-timeout marker. Got:\n{out}"
