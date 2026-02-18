"""G1 — First TinyGo user-space program test.

Boots a kernel with the go_test feature and asserts that the Go user
program successfully prints the GOUSR: ok marker via sys_debug_write.
"""


def test_go_user_ok(qemu_serial_go):
    """TinyGo user binary prints GOUSR: ok via syscall 0."""
    serial = qemu_serial_go.stdout
    assert "GOUSR: ok" in serial, (
        f"Expected 'GOUSR: ok' in serial output.\n"
        f"Full output:\n{serial}"
    )
