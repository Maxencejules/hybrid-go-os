import os
import subprocess

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ISO_PATH = os.path.join(REPO_ROOT, "out", "os.iso")
DISK_IMG = os.path.join(REPO_ROOT, "out", "test.img")
HELLO_BIN = os.path.join(REPO_ROOT, "out", "hello.bin")
MKDISK = os.path.join(REPO_ROOT, "tools", "mkdisk.py")
QEMU_TIMEOUT = 10  # seconds


@pytest.fixture
def qemu_serial():
    """Boot the OS in QEMU headless and return the captured serial output."""
    assert os.path.isfile(ISO_PATH), f"ISO not found: {ISO_PATH}"

    # Build SimpleFS disk image with hello.pkg (always rebuild)
    if os.path.isfile(HELLO_BIN):
        subprocess.run(["python3", MKDISK, HELLO_BIN, DISK_IMG], check=True)
    elif not os.path.isfile(DISK_IMG):
        with open(DISK_IMG, "wb") as f:
            f.write(b"\x00" * (1024 * 1024))

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
                "-drive", f"file={DISK_IMG},format=raw,if=none,id=disk0",
                "-device", "virtio-blk-pci,drive=disk0,disable-modern=on",
            ],
            capture_output=True,
            text=True,
            timeout=QEMU_TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode("utf-8", errors="replace") if exc.stdout else ""
        pytest.fail(f"QEMU timed out ({QEMU_TIMEOUT}s). Captured serial:\n{stdout}")

    return result
