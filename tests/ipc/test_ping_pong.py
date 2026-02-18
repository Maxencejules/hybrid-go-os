"""R4 acceptance test: IPC ping-pong between two user tasks."""


def test_ping_pong(qemu_serial_ipc):
    """Two user tasks exchange messages via IPC endpoints."""
    out = qemu_serial_ipc.stdout
    assert "PING: ok" in out, f"Missing 'PING: ok'. Got:\n{out}"
    assert "PONG: ok" in out, f"Missing 'PONG: ok'. Got:\n{out}"
