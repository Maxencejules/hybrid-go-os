"""Compatibility Profile v1 skeleton: time/signal subset."""

from pathlib import Path


def _profile_text():
    return (
        Path(__file__).resolve().parents[2] / "docs" / "abi" / "compat_profile_v1.md"
    ).read_text(encoding="utf-8")


def test_profile_declares_time_signal_subset():
    text = _profile_text()
    assert "### Time and signal subset (`required`)" in text


def test_clock_and_sleep_contract_todo(compat_todo):
    compat_todo("time/signal: clock_gettime + nanosleep baseline behavior")


def test_signal_delivery_contract_todo(compat_todo):
    compat_todo("time/signal: sigaction + kill deterministic delivery semantics")
