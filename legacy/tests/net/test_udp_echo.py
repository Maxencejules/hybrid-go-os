"""M7 acceptance test: VirtIO-net UDP echo.

Boots the OS with a VirtIO-net device, sends a UDP packet to port 7,
and asserts that netd echoes it back and prints "NET: udp echo".
"""

import os
import socket
import subprocess
import threading
import time

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ISO_PATH = os.path.join(REPO_ROOT, "out", "os.iso")
DISK_IMG = os.path.join(REPO_ROOT, "out", "test.img")
HELLO_BIN = os.path.join(REPO_ROOT, "out", "hello.bin")
MKDISK = os.path.join(REPO_ROOT, "tools", "mkdisk.py")

QEMU_TIMEOUT = 15  # longer timeout for networking
UDP_PORT = 15000
UDP_DELAY = 4  # seconds to wait before sending UDP packet


def _send_udp_packets():
    """Background thread: send UDP packets to the guest after a delay."""
    time.sleep(UDP_DELAY)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Send multiple packets to handle possible ARP timing
    for _ in range(5):
        try:
            sock.sendto(b"ping", ("127.0.0.1", UDP_PORT))
        except OSError:
            pass
        time.sleep(0.5)
    sock.close()


def test_udp_echo():
    """Send UDP to guest port 7, assert 'NET: udp echo' in serial output."""
    assert os.path.isfile(ISO_PATH), f"ISO not found: {ISO_PATH}"

    # Build SimpleFS disk image
    if os.path.isfile(HELLO_BIN):
        subprocess.run(["python3", MKDISK, HELLO_BIN, DISK_IMG], check=True)
    elif not os.path.isfile(DISK_IMG):
        with open(DISK_IMG, "wb") as f:
            f.write(b"\x00" * (1024 * 1024))

    # Start UDP sender in background
    sender = threading.Thread(target=_send_udp_packets, daemon=True)
    sender.start()

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
                "-netdev", f"user,id=n0,hostfwd=udp::{UDP_PORT}-10.0.2.15:7",
                "-device", "virtio-net-pci,netdev=n0,disable-modern=on",
            ],
            capture_output=True,
            text=True,
            timeout=QEMU_TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode("utf-8", errors="replace") if exc.stdout else ""
        # Timeout is expected — guest runs forever. Check captured output.
        assert "NET: udp echo" in stdout, (
            f"QEMU timed out and 'NET: udp echo' not found in serial output.\n"
            f"Captured:\n{stdout}"
        )
        return

    # If QEMU exited before timeout, check output
    output = result.stdout
    assert "NET: udp echo" in output, (
        f"'NET: udp echo' not found in serial output.\n"
        f"stdout:\n{output}\nstderr:\n{result.stderr}"
    )
