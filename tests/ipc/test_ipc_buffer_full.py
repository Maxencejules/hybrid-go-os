"""R4 acceptance test: IPC send returns -1 when single-slot buffer is occupied."""


def test_ipc_buffer_full(qemu_serial_ipc_buffer_full):
    """Send to an occupied endpoint returns -1; original message is preserved."""
    out = qemu_serial_ipc_buffer_full.stdout
    assert "IPC: full ok" in out, f"Missing 'IPC: full ok'. Got:\n{out}"
