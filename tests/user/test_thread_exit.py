"""M3 acceptance test: sys_thread_exit terminates user task cleanly."""


def test_thread_exit(qemu_serial_thread_exit):
    """User thread_exit syscall should terminate task and halt cleanly."""
    out = qemu_serial_thread_exit.stdout
    assert "THREAD_EXIT: ok" in out, f"Missing 'THREAD_EXIT: ok'. Got:\n{out}"
    assert "RUGO: halt ok" in out, (
        f"Kernel did not halt cleanly after sys_thread_exit. Got:\n{out}"
    )
