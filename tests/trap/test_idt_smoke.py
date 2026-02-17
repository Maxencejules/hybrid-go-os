"""M1 acceptance test: IDT handles a forced exception."""


def test_idt_smoke(qemu_serial_idt):
    """A forced int3 exception must produce a deterministic trap marker."""
    out = qemu_serial_idt.stdout
    assert "TRAP: ok" in out, f"Missing 'TRAP: ok'. Got:\n{out}"
