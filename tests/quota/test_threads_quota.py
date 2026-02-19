"""Quota acceptance: thread spawn is capped per process."""


def test_threads_quota(qemu_serial_quota_threads):
    """Ring3 thread spawns must fail with -1 exactly at quota limit."""
    out = qemu_serial_quota_threads.stdout
    assert "QUOTA: threads ok" in out, (
        f"Missing 'QUOTA: threads ok'. Got:\n{out}"
    )
