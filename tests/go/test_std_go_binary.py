"""G2 spike acceptance test: std-port candidate marker.

The current spike uses a TinyGo compatibility bridge while preserving the
GOOS/GOARCH contract (`rugo`/`amd64`) in docs and build metadata.
"""


def test_std_go_binary(qemu_serial_go_std):
    """Standard-Go user binary prints GOSTD: ok via syscall bridge."""
    serial = qemu_serial_go_std.stdout
    assert "GOSTD: ok" in serial, (
        "Expected 'GOSTD: ok' in serial output for G2 acceptance.\n"
        f"Full output:\n{serial}"
    )
