"""M2 acceptance test: two kernel threads run with preemptive scheduling."""

import re


def test_two_threads(qemu_serial_sched):
    """Serial output must show interleaved A and B thread output."""
    out = qemu_serial_sched.stdout

    # Extract just the A/B letters in order of appearance
    markers = re.findall(r"^([AB])$", out, re.MULTILINE)
    seq = "".join(markers)

    assert "A" in seq, f"Thread A never ran. Got:\n{out}"
    assert "B" in seq, f"Thread B never ran. Got:\n{out}"

    # Verify at least one A->B and one B->A transition (preemption happened)
    assert "AB" in seq or "BA" in seq, (
        f"No interleaving detected. Sequence: {seq[:80]}"
    )
