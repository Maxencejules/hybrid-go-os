"""M4 acceptance test: shared memory bulk transfer."""


def test_shm_bulk(qemu_serial):
    """Writer and reader must verify shared memory via checksum."""
    out = qemu_serial.stdout
    assert "SHM: checksum ok" in out, f"Missing 'SHM: checksum ok'. Got:\n{out}"
