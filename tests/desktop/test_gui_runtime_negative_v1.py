"""M51 PR-2: negative-path checks for GUI runtime/toolkit reports."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_gui_runtime_v1 as runtime  # noqa: E402
import run_toolkit_compat_v1 as compat  # noqa: E402


def _out_path(name: str) -> Path:
    path = ROOT / "out" / "pytest-m51" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    return path


def test_gui_runtime_v1_rejects_unknown_check_id():
    out = _out_path("gui-runtime-v1-error.json")
    rc = runtime.main(
        [
            "--inject-failure",
            "unknown-check-42",
            "--out",
            str(out),
        ]
    )
    assert rc == 2
    assert not out.exists()


def test_toolkit_compat_v1_rejects_unknown_case_id():
    out = _out_path("toolkit-compat-v1-error.json")
    rc = compat.main(
        [
            "--inject-render-failure",
            "unknown-case-42",
            "--out",
            str(out),
        ]
    )
    assert rc == 2
    assert not out.exists()
