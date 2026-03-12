"""M25 runtime-backed acceptance: real boot path consumes the service model."""


def _find_in_order(serial: str, markers: list[str]) -> None:
    pos = -1
    for marker in markers:
        pos = serial.find(marker, pos + 1)
        assert pos != -1, f"Missing '{marker}' in serial output.\nFull output:\n{serial}"


def test_userspace_model_v2_boots_manifest_driven_go_runtime(qemu_serial_go):
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
            "GOSVCM: class timesvc critical",
            "TIMESVC: start",
            "SVC: timesvc running",
            "TIMESVC: ready",
            "GOINIT: operational",
            "GOSVCM: shell",
            "SVC: shell starting",
            "GOSVCM: class shell best-effort",
            "GOSH: start",
            "GOSH: recycle",
            "GOSVCM: reap shell",
            "SVC: shell failed",
            "GOSVCM: restart shell",
            "SVC: shell starting",
            "GOSVCM: class shell best-effort",
            "GOSH: start",
            "GOSH: recycle",
            "GOSVCM: reap shell",
            "SVC: shell failed",
            "GOSVCM: restart shell",
            "SVC: shell starting",
            "GOSVCM: class shell best-effort",
            "GOSH: start",
            "GOSH: lookup ok",
            "GOSH: recv deny",
            "GOSH: reg deny",
            "GOSH: spawn deny",
            "SVC: shell running",
            "TIMESVC: req ok",
            "TIMESVC: time ok",
            "GOSH: reply ok",
            "SVC: shell stopping",
            "SVC: shell stopped",
            "SVC: timesvc stopping",
            "SVC: timesvc stopped",
            "GOSVCM: reap shell",
            "GOSVCM: stop diagsvc",
            "SVC: diagsvc stopping",
            "GOSVCM: reap timesvc",
            "DIAGSVC: stop",
            "SVC: diagsvc stopped",
            "GOSVCM: reap diagsvc",
            "GOINIT: ready",
            "RUGO: halt ok",
        ],
    )

    assert serial.count("SVC: shell starting") == 3
    assert serial.count("GOSVCM: class shell best-effort") == 3
    assert serial.count("GOSVCM: class timesvc critical") == 1
    assert serial.count("GOSVCM: restart shell") == 2
    assert serial.count("GOSVCM: reap shell") == 3
    assert serial.count("GOSH: recycle") == 2
    assert serial.count("SVC: shell failed") == 2

    assert serial.count("SVC: timesvc starting") == 1
    assert serial.count("SVC: timesvc running") == 1
    assert serial.count("SVC: shell running") == 3
    assert serial.count("SVC: shell stopped") == 1
    assert serial.count("SVC: timesvc stopped") == 1
    assert serial.count("GOSVCM: stop diagsvc") == 1
    assert serial.count("SVC: diagsvc stopped") == 1

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
