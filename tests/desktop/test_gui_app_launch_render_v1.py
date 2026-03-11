"""M51 PR-2: deterministic GUI app launch/render checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_gui_runtime_v1 as runtime  # noqa: E402


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def _out_path(name: str) -> Path:
    path = ROOT / "out" / "pytest-m51" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    return path


def test_gui_runtime_v1_is_seed_deterministic():
    first = runtime.run_gui_runtime(seed=20260311)
    second = runtime.run_gui_runtime(seed=20260311)
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_gui_runtime_v1_schema_and_app_launch_render():
    out = _out_path("gui-runtime-v1.json")
    rc = runtime.main(["--seed", "20260311", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    apps = {app["app_id"]: app for app in data["apps"]}

    assert data["schema"] == "rugo.gui_runtime_report.v1"
    assert data["contract_id"] == "rugo.gui_runtime_contract.v1"
    assert data["toolkit_profile_id"] == "rugo.toolkit_profile.v1"
    assert data["font_policy_id"] == "rugo.font_text_rendering_policy.v1"
    assert data["gate"] == "test-gui-runtime-v1"
    assert data["toolkit_gate"] == "test-toolkit-compat-v1"
    assert data["gate_pass"] is True
    assert data["total_failures"] == 0
    assert data["summary"]["launch"]["pass"] is True
    assert data["summary"]["render"]["pass"] is True
    assert data["runtime_topology"]["focus_owner"] == "settings.panel"
    assert data["runtime_topology"]["toolkit_profile_count"] == 2

    assert apps["desktop.shell.workspace"]["toolkit_profile"] == "rugo.widgets.retain.v1"
    assert apps["desktop.shell.workspace"]["state"] == "visible"
    assert apps["files.panel"]["state"] == "occluded"
    assert apps["settings.panel"]["state"] == "focused"
    assert apps["settings.panel"]["input_required"] is True
    assert apps["settings.panel"]["input_ok"] is True
    assert apps["toast.network"]["retired"] is True
    assert apps["toast.network"]["state"] == "destroyed"
    assert all(app["launch_ok"] for app in apps.values())
    assert all(app["render_ok"] for app in apps.values())


def test_gui_runtime_v1_detects_launch_regression():
    out = _out_path("gui-runtime-v1-launch-fail.json")
    rc = runtime.main(
        [
            "--inject-failure",
            "app_launch_budget",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert "app_launch_budget" in data["failures"]
    assert data["summary"]["launch"]["failures"] >= 1
