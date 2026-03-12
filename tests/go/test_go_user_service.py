"""G1 acceptance test: canonical Go userspace bootstrap path."""


def _find_in_order(serial: str, markers: list[str]) -> None:
    pos = -1
    for marker in markers:
        pos = serial.find(marker, pos + 1)
        assert pos != -1, (
            f"Expected '{marker}' in serial output.\n"
            f"Full output:\n{serial}"
        )


def test_go_userspace_bootstrap(qemu_serial_go):
    """Kernel boot must reach Go init, launcher, shell, and syscall-backed service."""
    serial = qemu_serial_go.stdout

    _find_in_order(
        serial,
        [
            "RUGO: boot ok",
            "GOINIT: start",
            "GOINIT: bootstrap",
            "GOINIT: svcmgr up",
            "GOSVCM: start",
            "SVC: timesvc declared",
            "SVC: shell declared",
            "SVC: timesvc starting",
            "TIMESVC: start",
            "SVC: timesvc running",
            "TIMESVC: ready",
            "GOINIT: operational",
            "GOSVCM: shell",
            "GOSH: recycle",
            "GOSVCM: restart shell",
            "GOSH: lookup ok",
            "GOSH: recv deny",
            "GOSH: reg deny",
            "GOSH: spawn deny",
            "TIMESVC: req ok",
            "TIMESVC: time ok",
            "GOSH: reply ok",
            "GOSVCM: reap timesvc",
            "GOINIT: ready",
            "RUGO: halt ok",
        ],
    )

    assert serial.count("GOSH: recycle") == 2, (
        "Expected two shell recycle attempts before the successful run.\n"
        f"Full output:\n{serial}"
    )

    for error_marker in (
        "GOINIT: err",
        "GOSVCM: err",
        "TIMESVC: err",
        "GOSH: err",
    ):
        assert error_marker not in serial, (
            f"Did not expect '{error_marker}' in serial output.\n"
            f"Full output:\n{serial}"
        )
