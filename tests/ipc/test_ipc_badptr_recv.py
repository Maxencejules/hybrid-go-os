"""R4 acceptance test: IPC recv with invalid user pointer returns -1."""


def test_ipc_badptr_recv(qemu_serial_ipc_badptr_recv):
    """sys_ipc_recv with unmapped buffer returns -1 and kernel does not crash."""
    out = qemu_serial_ipc_badptr_recv.stdout
    assert "IPC: badptr recv ok" in out, f"Missing 'IPC: badptr recv ok'. Got:\n{out}"
