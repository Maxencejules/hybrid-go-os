"""M3 acceptance test: sys_thread_spawn creates a runnable user thread."""


def test_thread_spawn(qemu_serial_thread_spawn):
    """Spawned user thread should run, then main thread should resume."""
    out = qemu_serial_thread_spawn.stdout
    assert "SPAWN: child ok" in out, (
        f"Missing 'SPAWN: child ok' marker. Got:\n{out}"
    )
    assert "SPAWN: main ok" in out, (
        f"Missing 'SPAWN: main ok' marker. Got:\n{out}"
    )
    assert "SPAWN: spawn err" not in out, (
        f"Unexpected spawn failure marker. Got:\n{out}"
    )
