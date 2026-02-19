"""Quota acceptance: endpoint creation is capped per process."""


def test_endpoints_quota(qemu_serial_quota_endpoints):
    """Ring3 endpoint creates must fail with -1 exactly at quota limit."""
    out = qemu_serial_quota_endpoints.stdout
    assert "QUOTA: endpoints ok" in out, (
        f"Missing 'QUOTA: endpoints ok'. Got:\n{out}"
    )
