"""Compatibility Profile v1: file I/O executable checks."""

from pathlib import Path

import sys

sys.path.append(str(Path(__file__).resolve().parent))

from v1_model import FdTableModel


def _profile_text():
    return (
        Path(__file__).resolve().parents[2] / "docs" / "abi" / "compat_profile_v1.md"
    ).read_text(encoding="utf-8")


def test_profile_declares_file_io_subset():
    text = _profile_text()
    assert "### File I/O subset (`required`)" in text


def test_open_read_write_close_contract():
    model = FdTableModel()
    fd = model.open("/compat/hello.txt")
    assert fd >= 3

    n1, chunk1 = model.read(fd, 6)
    assert n1 == 6
    assert chunk1 == b"compat"

    n2, chunk2 = model.read(fd, 64)
    assert n2 > 0
    assert chunk2.endswith(b"\n")

    assert model.close(fd) == 0
    assert model.close(fd) == -1


def test_fd_offset_and_metadata_contract():
    model = FdTableModel()
    cfd = model.open("/dev/console")
    assert cfd >= 3
    assert model.write(cfd, b"ok") == 2
    assert bytes(model.console_log) == b"ok"

    missing_fd = 99
    n, data = model.read(missing_fd, 4)
    assert n == -1
    assert data == b""
