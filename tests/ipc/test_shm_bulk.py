"""R4 acceptance test: shared memory bulk data transfer."""


def test_shm_bulk(qemu_serial_shm):
    """Writer fills shared memory, reader verifies checksum."""
    out = qemu_serial_shm.stdout
    assert "SHM: checksum ok" in out, f"Missing 'SHM: checksum ok'. Got:\n{out}"
