"""M3 acceptance test: invalid syscall returns -1 and kernel stays alive."""


def test_syscall_invalid(_boot_iso_syscall_invalid):
    """Unknown syscall must return -1 and print the pass marker."""
    out = _boot_iso_syscall_invalid.stdout
    assert "SYSCALL: invalid ok" in out, (
        f"Missing 'SYSCALL: invalid ok'. Got:\n{out}"
    )
