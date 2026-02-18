"""R4 acceptance test: IPC send with invalid user pointer returns -1."""


def test_ipc_badptr_send(qemu_serial_ipc_badptr_send):
    """sys_ipc_send with unmapped buffer returns -1 and kernel does not crash."""
    out = qemu_serial_ipc_badptr_send.stdout
    assert "IPC: badptr send ok" in out, f"Missing 'IPC: badptr send ok'. Got:\n{out}"
