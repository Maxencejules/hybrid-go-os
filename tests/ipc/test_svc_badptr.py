"""R4 acceptance test: service registry with invalid user pointer returns -1."""


def test_svc_badptr(qemu_serial_svc_badptr):
    """sys_svc_register with unmapped name pointer returns -1 and kernel does not crash."""
    out = qemu_serial_svc_badptr.stdout
    assert "SVC: badptr ok" in out, f"Missing 'SVC: badptr ok'. Got:\n{out}"
