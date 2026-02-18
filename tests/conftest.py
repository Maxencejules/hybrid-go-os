import os
import socket
import subprocess
import threading
import time

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ISO_PATH = os.path.join(REPO_ROOT, "out", "os.iso")
ISO_PANIC_PATH = os.path.join(REPO_ROOT, "out", "os-panic.iso")
ISO_PF_PATH = os.path.join(REPO_ROOT, "out", "os-pf.iso")
ISO_IDT_PATH = os.path.join(REPO_ROOT, "out", "os-idt.iso")
ISO_SCHED_PATH = os.path.join(REPO_ROOT, "out", "os-sched.iso")
ISO_USER_HELLO_PATH = os.path.join(REPO_ROOT, "out", "os-user-hello.iso")
ISO_SYSCALL_PATH = os.path.join(REPO_ROOT, "out", "os-syscall.iso")
ISO_USER_FAULT_PATH = os.path.join(REPO_ROOT, "out", "os-user-fault.iso")
ISO_IPC_PATH = os.path.join(REPO_ROOT, "out", "os-ipc.iso")
ISO_IPC_BADPTR_SEND_PATH = os.path.join(REPO_ROOT, "out", "os-ipc-badptr-send.iso")
ISO_IPC_BADPTR_SVC_PATH = os.path.join(REPO_ROOT, "out", "os-ipc-badptr-svc.iso")
ISO_IPC_BUFFER_FULL_PATH = os.path.join(REPO_ROOT, "out", "os-ipc-buffer-full.iso")
ISO_SHM_PATH = os.path.join(REPO_ROOT, "out", "os-shm.iso")
ISO_BLK_PATH = os.path.join(REPO_ROOT, "out", "os-blk.iso")
BLK_DISK_IMG = os.path.join(REPO_ROOT, "out", "blk-test.img")
ISO_FS_PATH = os.path.join(REPO_ROOT, "out", "os-fs.iso")
FS_DISK_IMG = os.path.join(REPO_ROOT, "out", "fs-test.img")
ISO_NET_PATH = os.path.join(REPO_ROOT, "out", "os-net.iso")
ISO_GO_PATH = os.path.join(REPO_ROOT, "out", "os-go.iso")
QEMU_TIMEOUT = 10  # seconds
NET_TIMEOUT = 15   # longer timeout for networking


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


@pytest.fixture
def qemu_serial_sched():
    """Boot the scheduler-test OS image and return captured serial output."""
    if not os.path.isfile(ISO_SCHED_PATH):
        pytest.skip(f"ISO not built: {ISO_SCHED_PATH}")
    return _boot_iso(ISO_SCHED_PATH)


@pytest.fixture
def qemu_serial_user_hello():
    """Boot the user-hello-test OS image and return captured serial output."""
    if not os.path.isfile(ISO_USER_HELLO_PATH):
        pytest.skip(f"ISO not built: {ISO_USER_HELLO_PATH}")
    return _boot_iso(ISO_USER_HELLO_PATH)


@pytest.fixture
def qemu_serial_syscall():
    """Boot the syscall-test OS image and return captured serial output."""
    if not os.path.isfile(ISO_SYSCALL_PATH):
        pytest.skip(f"ISO not built: {ISO_SYSCALL_PATH}")
    return _boot_iso(ISO_SYSCALL_PATH)


@pytest.fixture
def qemu_serial_user_fault():
    """Boot the user-fault-test OS image and return captured serial output."""
    if not os.path.isfile(ISO_USER_FAULT_PATH):
        pytest.skip(f"ISO not built: {ISO_USER_FAULT_PATH}")
    return _boot_iso(ISO_USER_FAULT_PATH)


@pytest.fixture
def qemu_serial_ipc():
    """Boot the IPC ping-pong test OS image and return captured serial output."""
    if not os.path.isfile(ISO_IPC_PATH):
        pytest.skip(f"ISO not built: {ISO_IPC_PATH}")
    return _boot_iso(ISO_IPC_PATH)


@pytest.fixture
def qemu_serial_ipc_badptr_send():
    """Boot the IPC bad-pointer send test OS image and return captured serial output."""
    if not os.path.isfile(ISO_IPC_BADPTR_SEND_PATH):
        pytest.skip(f"ISO not built: {ISO_IPC_BADPTR_SEND_PATH}")
    return _boot_iso(ISO_IPC_BADPTR_SEND_PATH)


@pytest.fixture
def qemu_serial_ipc_badptr_svc():
    """Boot the IPC bad-pointer service registry test OS image and return captured serial output."""
    if not os.path.isfile(ISO_IPC_BADPTR_SVC_PATH):
        pytest.skip(f"ISO not built: {ISO_IPC_BADPTR_SVC_PATH}")
    return _boot_iso(ISO_IPC_BADPTR_SVC_PATH)


@pytest.fixture
def qemu_serial_ipc_buffer_full():
    """Boot the IPC buffer-full test OS image and return captured serial output."""
    if not os.path.isfile(ISO_IPC_BUFFER_FULL_PATH):
        pytest.skip(f"ISO not built: {ISO_IPC_BUFFER_FULL_PATH}")
    return _boot_iso(ISO_IPC_BUFFER_FULL_PATH)


@pytest.fixture
def qemu_serial_shm():
    """Boot the SHM bulk test OS image and return captured serial output."""
    if not os.path.isfile(ISO_SHM_PATH):
        pytest.skip(f"ISO not built: {ISO_SHM_PATH}")
    return _boot_iso(ISO_SHM_PATH)


def _boot_iso_with_disk(iso_path, disk_path):
    """Boot an ISO in QEMU with a virtio-blk disk attached."""
    assert os.path.isfile(iso_path), f"ISO not found: {iso_path}"

    # Create a 1 MiB raw disk image if it doesn't exist
    if not os.path.isfile(disk_path):
        with open(disk_path, "wb") as f:
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
                "-cdrom", iso_path,
                "-drive", f"file={disk_path},format=raw,if=none,id=disk0",
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


@pytest.fixture
def qemu_serial_blk():
    """Boot the VirtIO block test OS image with a raw disk attached."""
    if not os.path.isfile(ISO_BLK_PATH):
        pytest.skip(f"ISO not built: {ISO_BLK_PATH}")
    return _boot_iso_with_disk(ISO_BLK_PATH, BLK_DISK_IMG)


@pytest.fixture
def qemu_serial_fs():
    """Boot the FS test OS image with a formatted SimpleFS disk attached."""
    if not os.path.isfile(ISO_FS_PATH):
        pytest.skip(f"ISO not built: {ISO_FS_PATH}")
    if not os.path.isfile(FS_DISK_IMG):
        pytest.skip(f"Disk image not built: {FS_DISK_IMG}")
    return _boot_iso_with_disk(ISO_FS_PATH, FS_DISK_IMG)


def _find_free_udp_port():
    """Find a free UDP port on localhost."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _boot_iso_with_net(iso_path):
    """Boot an ISO in QEMU with virtio-net and inject a UDP echo packet."""
    assert os.path.isfile(iso_path), f"ISO not found: {iso_path}"

    udp_port = _find_free_udp_port()

    proc = subprocess.Popen(
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
            "-netdev", f"user,id=n0,hostfwd=udp::{udp_port}-10.0.2.15:7",
            "-device", "virtio-net-pci,netdev=n0,disable-modern=on",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    def _send_udp():
        """Send UDP packets after a boot delay to trigger the echo."""
        time.sleep(3)
        for _ in range(5):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(b"echo test", ("127.0.0.1", udp_port))
                sock.close()
            except OSError:
                pass
            time.sleep(0.5)

    sender = threading.Thread(target=_send_udp, daemon=True)
    sender.start()

    try:
        stdout, stderr = proc.communicate(timeout=NET_TIMEOUT)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        stdout_str = stdout.decode("utf-8", errors="replace") if stdout else ""
        pytest.fail(
            f"QEMU timed out ({NET_TIMEOUT}s). Captured serial:\n{stdout_str}"
        )

    return subprocess.CompletedProcess(
        args=proc.args,
        returncode=proc.returncode,
        stdout=stdout.decode("utf-8", errors="replace") if stdout else "",
        stderr=stderr.decode("utf-8", errors="replace") if stderr else "",
    )


@pytest.fixture
def qemu_serial_net():
    """Boot the VirtIO net test OS image with networking."""
    if not os.path.isfile(ISO_NET_PATH):
        pytest.skip(f"ISO not built: {ISO_NET_PATH}")
    return _boot_iso_with_net(ISO_NET_PATH)


@pytest.fixture
def qemu_serial_go():
    """Boot the G1 TinyGo user-space test OS image."""
    if not os.path.isfile(ISO_GO_PATH):
        pytest.skip(f"ISO not built: {ISO_GO_PATH}")
    return _boot_iso(ISO_GO_PATH)
