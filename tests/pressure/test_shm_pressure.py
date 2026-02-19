"""SHM pressure acceptance: deterministic create/map/unmap until resource cap."""


def test_shm_pressure(qemu_serial_pressure_shm):
    """Kernel must handle SHM pressure and print success marker."""
    out = qemu_serial_pressure_shm.stdout
    assert "PRESSURE: shm ok" in out, (
        f"Missing 'PRESSURE: shm ok'. Got:\n{out}"
    )
