import os
import subprocess

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ISO_PATH = os.path.join(REPO_ROOT, "out", "os.iso")
ISO_PANIC_PATH = os.path.join(REPO_ROOT, "out", "os-panic.iso")
ISO_PF_PATH = os.path.join(REPO_ROOT, "out", "os-pf.iso")
ISO_IDT_PATH = os.path.join(REPO_ROOT, "out", "os-idt.iso")
QEMU_TIMEOUT = 10  # seconds


def _boot_iso(iso_path):
    """Boot an ISO in QEMU headless and return the CompletedProcess."""
    assert os.path.isfile(iso_path), f"ISO not found: {iso_path}"

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
                "-cdrom", iso_path,
            ],
            capture_output=True,
            text=True,
            timeout=QEMU_TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode("utf-8", errors="replace") if exc.stdout else ""
        pytest.fail(f"QEMU timed out ({QEMU_TIMEOUT}s). Captured serial:\n{stdout}")

    return result


@pytest.fixture
def qemu_serial():
    """Boot the normal OS image and return captured serial output."""
    return _boot_iso(ISO_PATH)


@pytest.fixture
def qemu_serial_panic():
    """Boot the panic-test OS image and return captured serial output."""
    return _boot_iso(ISO_PANIC_PATH)


@pytest.fixture
def qemu_serial_pf():
    """Boot the page-fault-test OS image and return captured serial output."""
    if not os.path.isfile(ISO_PF_PATH):
        pytest.skip(f"ISO not built: {ISO_PF_PATH}")
    return _boot_iso(ISO_PF_PATH)


@pytest.fixture
def qemu_serial_idt():
    """Boot the IDT-smoke-test OS image and return captured serial output."""
    if not os.path.isfile(ISO_IDT_PATH):
        pytest.skip(f"ISO not built: {ISO_IDT_PATH}")
    return _boot_iso(ISO_IDT_PATH)
