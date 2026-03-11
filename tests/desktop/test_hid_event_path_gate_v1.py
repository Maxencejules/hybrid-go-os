"""M49 aggregate sub-gate: HID event-path wiring and artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_hid_event_path_v1 as hid  # noqa: E402
import run_input_seat_runtime_v1 as runtime  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _out_path(name: str) -> Path:
    path = ROOT / "out" / "pytest-m49" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    return path


def test_hid_event_path_gate_v1_wiring_and_artifacts():
    required = [
        "docs/M49_EXECUTION_BACKLOG.md",
        "docs/desktop/seat_input_contract_v1.md",
        "docs/desktop/input_event_contract_v1.md",
        "docs/desktop/focus_routing_policy_v1.md",
        "tools/run_input_seat_runtime_v1.py",
        "tools/run_hid_event_path_v1.py",
        "tests/desktop/test_input_seat_docs_v1.py",
        "tests/desktop/test_keyboard_event_delivery_v1.py",
        "tests/desktop/test_pointer_motion_buttons_v1.py",
        "tests/desktop/test_focus_routing_v1.py",
        "tests/desktop/test_seat_hotplug_v1.py",
        "tests/desktop/test_hid_event_path_gate_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M49 sub-gate artifact: {rel}"

    roadmap = _read("docs/M48_M52_GUI_IMPLEMENTATION_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M49_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-hid-event-path-v1" in roadmap

    assert "test-hid-event-path-v1" in makefile
    for entry in [
        "tools/run_input_seat_runtime_v1.py --out $(OUT)/input-seat-v1.json",
        "tools/run_hid_event_path_v1.py --out $(OUT)/hid-event-path-v1.json",
        "tests/desktop/test_input_seat_docs_v1.py",
        "tests/desktop/test_keyboard_event_delivery_v1.py",
        "tests/desktop/test_pointer_motion_buttons_v1.py",
        "tests/desktop/test_focus_routing_v1.py",
        "tests/desktop/test_seat_hotplug_v1.py",
        "tests/desktop/test_hid_event_path_gate_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-hid-event-path-v1.xml" in makefile

    assert "HID event path v1 gate" in ci
    assert "make test-hid-event-path-v1" in ci
    assert "hid-event-path-v1-artifacts" in ci
    assert "out/pytest-hid-event-path-v1.xml" in ci
    assert "out/input-seat-v1.json" in ci
    assert "out/hid-event-path-v1.json" in ci

    assert "Status: done" in backlog
    assert "| M49 | Input + Seat Management v1 | n/a | done |" in milestones
    assert "| **M49** Input + Seat Management v1 | n/a | done |" in status
    assert "docs/architecture/SOURCE_MAP.md" in readme
    assert "docs/archive/README.md" in readme

    runtime_out = _out_path("hid-gate-input-seat-v1.json")
    hid_out = _out_path("hid-gate-event-path-v1.json")

    assert runtime.main(["--seed", "20260311", "--out", str(runtime_out)]) == 0
    assert hid.main(["--seed", "20260311", "--out", str(hid_out)]) == 0

    runtime_data = json.loads(runtime_out.read_text(encoding="utf-8"))
    hid_data = json.loads(hid_out.read_text(encoding="utf-8"))

    assert runtime_data["schema"] == "rugo.input_seat_runtime_report.v1"
    assert runtime_data["summary"]["delivery"]["pass"] is True
    assert runtime_data["summary"]["focus"]["pass"] is True
    assert runtime_data["gate_pass"] is True

    assert hid_data["schema"] == "rugo.hid_event_path_report.v1"
    assert hid_data["keyboard_path"]["path_checks_pass"] is True
    assert hid_data["pointer_path"]["path_checks_pass"] is True
    assert hid_data["hotplug_path"]["path_checks_pass"] is True
    assert hid_data["gate_pass"] is True
