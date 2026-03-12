"""M10 runtime-backed acceptance: default Go services observe policy denials."""


def test_go_service_lane_exposes_rights_denials(qemu_serial_go):
    serial = qemu_serial_go.stdout

    markers = [
        "GOSH: lookup ok",
        "GOSH: recv deny",
        "GOSH: reg deny",
        "GOSH: spawn deny",
        "GOSH: reply ok",
    ]

    positions = []
    for marker in markers:
        assert marker in serial, f"Missing '{marker}' in serial output.\nFull output:\n{serial}"
        positions.append(serial.index(marker))

    assert positions == sorted(positions), (
        "Expected Go service policy-denial markers in order.\n"
        f"Full output:\n{serial}"
    )

    assert "GOSH: err" not in serial, f"Unexpected shell error marker.\nFull output:\n{serial}"
