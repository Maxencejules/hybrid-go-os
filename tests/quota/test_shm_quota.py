"""Quota acceptance: SHM create is capped per process."""


def test_shm_quota(qemu_serial_quota_shm):
    """Ring3 SHM creates must fail with -1 exactly at quota limit."""
    out = qemu_serial_quota_shm.stdout
    assert "QUOTA: shm ok" in out, (
        f"Missing 'QUOTA: shm ok'. Got:\n{out}"
    )
