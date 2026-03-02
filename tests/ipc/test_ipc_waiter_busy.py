"""R4 acceptance test: second waiter and truncation edge cases return -1."""


def test_ipc_waiter_busy(qemu_serial_ipc_waiter_busy):
    """Kernel must reject second waiter and non-conforming send lengths."""
    out = qemu_serial_ipc_waiter_busy.stdout
    assert "IPC: waiter strict ok" in out, (
        f"Missing 'IPC: waiter strict ok'. Got:\n{out}"
    )
