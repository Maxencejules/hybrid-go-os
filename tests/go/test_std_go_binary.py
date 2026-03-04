"""G2 acceptance test: stock-Go contract marker path."""

from pathlib import Path


def test_std_go_binary(qemu_serial_go_std):
    """Standard-Go user binary prints marker set via syscall bridges."""
    serial = qemu_serial_go_std.stdout
    assert "GOSTD: ok" in serial, (
        "Expected 'GOSTD: ok' in serial output for G2 acceptance.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: time ok" in serial, (
        "Expected 'GOSTD: time ok' in serial output for G2 syscall bridge.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: yield ok" in serial, (
        "Expected 'GOSTD: yield ok' in serial output for G2 syscall bridge.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: vm ok" in serial, (
        "Expected 'GOSTD: vm ok' in serial output for G2 vm bridge.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: spawn child ok" in serial, (
        "Expected child-thread marker for G2 thread-spawn bridge.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: spawn main ok" in serial, (
        "Expected parent-thread marker after G2 thread-spawn bridge.\n"
        f"Full output:\n{serial}"
    )
    assert "THREAD_EXIT: ok" in serial, (
        "Expected kernel thread-exit marker after G2 sys_thread_exit call.\n"
        f"Full output:\n{serial}"
    )
    assert "RUGO: halt ok" in serial, (
        "Expected clean kernel halt after G2 sys_thread_exit call.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: time err" not in serial, (
        "Did not expect 'GOSTD: time err'; sys_time_now bridge failed.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: yield err" not in serial, (
        "Did not expect 'GOSTD: yield err'; sys_yield bridge failed.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: vm err" not in serial, (
        "Did not expect 'GOSTD: vm err'; vm bridge failed.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: spawn err" not in serial, (
        "Did not expect 'GOSTD: spawn err'; thread-spawn bridge failed.\n"
        f"Full output:\n{serial}"
    )
    assert "GOSTD: exit err" not in serial, (
        "Did not expect 'GOSTD: exit err'; sys_thread_exit should not return.\n"
        f"Full output:\n{serial}"
    )

    contract = (
        Path(__file__).resolve().parents[2] / "out" / "gostd-contract.env"
    ).read_text(encoding="utf-8")
    assert "GOOS=rugo" in contract, (
        "Expected GOOS=rugo in out/gostd-contract.env.\n"
        f"Contract contents:\n{contract}"
    )
    assert "GOARCH=amd64" in contract, (
        "Expected GOARCH=amd64 in out/gostd-contract.env.\n"
        f"Contract contents:\n{contract}"
    )
    assert "STOCK_GO_VERSION=go" in contract, (
        "Expected stock Go version metadata in out/gostd-contract.env.\n"
        f"Contract contents:\n{contract}"
    )
    assert "STOCK_GO_HOST_GOOS=" in contract, (
        "Expected host GOOS metadata in out/gostd-contract.env.\n"
        f"Contract contents:\n{contract}"
    )
    assert "STOCK_GO_HOST_GOARCH=" in contract, (
        "Expected host GOARCH metadata in out/gostd-contract.env.\n"
        f"Contract contents:\n{contract}"
    )
    assert "TINYGO_COMPAT_GOOS=" not in contract, (
        "Did not expect TinyGo compat metadata in stock-Go contract.\n"
        f"Contract contents:\n{contract}"
    )
