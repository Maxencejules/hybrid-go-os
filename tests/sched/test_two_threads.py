"""M2 acceptance test: two threads interleave on serial output."""

import re


def test_two_threads(qemu_serial):
    """Serial output must contain both A and B characters, interleaved."""
    out = qemu_serial.stdout
    assert "A" in out, f"Thread A never ran. Got:\n{out}"
    assert "B" in out, f"Thread B never ran. Got:\n{out}"
    # Verify interleaving: at least one A→B or B→A transition
    assert re.search(r"AB|BA", out), f"No interleaving found. Got:\n{out}"
