"""Compatibility Profile v1 skeleton: file I/O subset."""

from pathlib import Path


def _profile_text():
    return (
        Path(__file__).resolve().parents[2] / "docs" / "abi" / "compat_profile_v1.md"
    ).read_text(encoding="utf-8")


def test_profile_declares_file_io_subset():
    text = _profile_text()
    assert "### File I/O subset (`required`)" in text


def test_open_read_write_close_contract_todo(compat_todo):
    compat_todo("file I/O: open/openat/read/write/close baseline semantics")


def test_fd_offset_and_metadata_contract_todo(compat_todo):
    compat_todo("file I/O: lseek + stat/fstat + deterministic bad-fd behavior")
