"""Stress IPC acceptance: multi-task ring3 send/recv loops."""


def test_ipc_loop(qemu_serial_stress_ipc):
    """Kernel must survive deterministic IPC stress and print success marker."""
    out = qemu_serial_stress_ipc.stdout
    assert "STRESS: ipc ok" in out, (
        f"Missing 'STRESS: ipc ok'. Got:\n{out}"
    )
