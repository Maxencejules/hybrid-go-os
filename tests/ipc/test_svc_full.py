"""R4 acceptance test: service table full returns -1 on new unique name."""


def test_svc_full(qemu_serial_svc_full):
    """After 4 unique registrations, a 5th unique name must fail with -1."""
    out = qemu_serial_svc_full.stdout
    assert "SVC: full ok" in out, f"Missing 'SVC: full ok'. Got:\n{out}"
