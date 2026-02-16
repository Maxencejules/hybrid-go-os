import os
import subprocess

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ISO_PATH = os.path.join(REPO_ROOT, "out", "os.iso")
QEMU_TIMEOUT = 10  # seconds


@pytest.fixture
def qemu_serial():
    """Boot the OS in QEMU headless and return the captured serial output."""
    assert os.path.isfile(ISO_PATH), f"ISO not found: {ISO_PATH}"

    try:
        result = subprocess.run(
            [
                "qemu-system-x86_64",
                "-machine", "q35",
                "-cpu", "qemu64",
                "-m", "128",
                "-serial", "stdio",
                "-display", "none",
                "-no-reboot",
                "-device", "isa-debug-exit,iobase=0xf4,iosize=0x04",
                "-cdrom", ISO_PATH,
            ],
            capture_output=True,
            text=True,
            timeout=QEMU_TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode("utf-8", errors="replace") if exc.stdout else ""
        pytest.fail(f"QEMU timed out ({QEMU_TIMEOUT}s). Captured serial:\n{stdout}")

    return result
