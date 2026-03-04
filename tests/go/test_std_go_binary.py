"""G2 spike acceptance test: std-port candidate marker.

The current spike uses a TinyGo compatibility bridge while preserving the
GOOS/GOARCH contract (`rugo`/`amd64`) in docs and build metadata.
"""


def test_std_go_binary(qemu_serial_go_std):
    """Standard-Go user binary prints marker set via syscall bridges."""
    serial = qemu_serial_go_std.stdout
    assert "GOSTD: ok" in serial, (
        "Expected 'GOSTD: ok' in serial output for G2 acceptance.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: time ok" in serial, (
        "Expected 'GOSTD: time ok' in serial output for G2 syscall bridge.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: yield ok" in serial, (
        "Expected 'GOSTD: yield ok' in serial output for G2 syscall bridge.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: vm ok" in serial, (
        "Expected 'GOSTD: vm ok' in serial output for G2 vm bridge.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: spawn child ok" in serial, (
        "Expected child-thread marker for G2 thread-spawn bridge.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: spawn main ok" in serial, (
        "Expected parent-thread marker after G2 thread-spawn bridge.\n"
        f"Full output:\n{serial}"
    )
    assert "THREAD_EXIT: ok" in serial, (
        "Expected kernel thread-exit marker after G2 sys_thread_exit call.\n"
        f"Full output:\n{serial}"
    )
    assert "RUGO: halt ok" in serial, (
        "Expected clean kernel halt after G2 sys_thread_exit call.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: time err" not in serial, (
        "Did not expect 'GOSTD: time err'; sys_time_now bridge failed.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: yield err" not in serial, (
        "Did not expect 'GOSTD: yield err'; sys_yield bridge failed.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: vm err" not in serial, (
        "Did not expect 'GOSTD: vm err'; vm bridge failed.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: spawn err" not in serial, (
        "Did not expect 'GOSTD: spawn err'; thread-spawn bridge failed.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: exit err" not in serial, (
        "Did not expect 'GOSTD: exit err'; sys_thread_exit should not return.\n"
        f"Full output:\n{serial}"
    )
