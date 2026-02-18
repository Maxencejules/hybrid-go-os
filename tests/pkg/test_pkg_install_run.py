"""M6 acceptance test: Package install and app execution."""


def test_pkg_install_run(qemu_serial_fs):
    """Install hello.pkg, run hello, verify output."""
    out = qemu_serial_fs.stdout
    assert "APP: hello world" in out, (
        f"Missing 'APP: hello world'. Got:\n{out}"
    )
