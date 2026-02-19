"""R4 acceptance test: duplicate svc_register overwrites endpoint deterministically."""


def test_svc_overwrite(qemu_serial_svc_overwrite):
    """Register same name twice; lookup returns the second endpoint."""
    out = qemu_serial_svc_overwrite.stdout
    assert "SVC: overwrite ok" in out, f"Missing 'SVC: overwrite ok'. Got:\n{out}"
