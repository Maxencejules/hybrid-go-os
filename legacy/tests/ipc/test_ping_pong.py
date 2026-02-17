"""M4 acceptance test: ping-pong IPC."""


def test_ping_pong(qemu_serial):
    """Ping and pong processes must exchange messages via IPC."""
    out = qemu_serial.stdout
    assert "PING: ok" in out, f"Missing 'PING: ok'. Got:\n{out}"
    assert "PONG: ok" in out, f"Missing 'PONG: ok'. Got:\n{out}"
