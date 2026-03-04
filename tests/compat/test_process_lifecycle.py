"""Compatibility Profile v1 skeleton: process lifecycle subset."""

from pathlib import Path


def _profile_text():
    return (
        Path(__file__).resolve().parents[2] / "docs" / "abi" / "compat_profile_v1.md"
    ).read_text(encoding="utf-8")


def test_profile_declares_process_subset():
    text = _profile_text()
    assert "### Process lifecycle subset (`required`)" in text


def test_exec_argv_envp_contract_todo(compat_todo):
    compat_todo("process lifecycle: execve-style argv/envp delivery contract")


def test_exit_wait_status_contract_todo(compat_todo):
    compat_todo("process lifecycle: _exit/exit and wait/waitpid semantics")
