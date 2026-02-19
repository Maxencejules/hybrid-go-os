"""M6 acceptance test: PKG payload SHA-256 verification."""


def test_pkg_hash(qemu_serial_pkg_hash):
    """PKG payload hash must verify before app execution."""
    out = qemu_serial_pkg_hash.stdout
    assert "PKG: hash ok" in out, (
        f"Missing 'PKG: hash ok'. Got:\n{out}"
    )
