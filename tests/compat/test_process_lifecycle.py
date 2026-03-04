"""Compatibility Profile v1: process lifecycle executable checks."""

from pathlib import Path

import sys

sys.path.append(str(Path(__file__).resolve().parent))

from v1_model import ProcessModel


def _profile_text():
    return (
        Path(__file__).resolve().parents[2] / "docs" / "abi" / "compat_profile_v1.md"
    ).read_text(encoding="utf-8")


def test_profile_declares_process_subset():
    text = _profile_text()
    assert "### Process lifecycle subset (`required`)" in text


def test_exec_argv_envp_contract():
    model = ProcessModel()
    assert model.execve(["/bin/demo", "arg1"], ["A=1", "B=2"]) == 0

    startup = model.startup_contract()
    assert startup["argv"] == ["/bin/demo", "arg1", None]
    assert startup["envp"] == ["A=1", "B=2", None]
    assert startup["auxv"][-1] == ("AT_NULL", 0)


def test_exit_wait_status_contract():
    model = ProcessModel()
    assert model.execve(["/bin/demo"], []) == 0
    assert model.exit(7) == 0

    pid, status = model.waitpid(-1)
    assert pid == 1
    assert status == 7

    pid2, status2 = model.waitpid(-1)
    assert pid2 == -1
    assert status2 is None
