"""M10 acceptance: per-handle rights enforcement."""


def test_security_rights_enforcement(qemu_serial_sec_rights):
    """Kernel must enforce rights reduction/transfer semantics deterministically."""
    out = qemu_serial_sec_rights.stdout
    assert "SEC: rights ok" in out, (
        f"Missing 'SEC: rights ok'. Got:\n{out}"
    )
