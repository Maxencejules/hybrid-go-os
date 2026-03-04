"""Compatibility Profile v1 skeleton: socket API subset."""

from pathlib import Path


def _profile_text():
    return (
        Path(__file__).resolve().parents[2] / "docs" / "abi" / "compat_profile_v1.md"
    ).read_text(encoding="utf-8")


def test_profile_declares_socket_subset():
    text = _profile_text()
    assert "### Socket API subset (`required`)" in text


def test_socket_lifecycle_contract_todo(compat_todo):
    compat_todo("socket API: socket/bind/listen/accept/connect/send/recv semantics")


def test_readiness_wait_contract_todo(compat_todo):
    compat_todo("socket API: poll or equivalent readiness-wait semantics")
