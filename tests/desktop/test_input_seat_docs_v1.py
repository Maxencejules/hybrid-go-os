"""M49 PR-1: input seat contract doc checks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_m49_pr1_input_seat_artifacts_exist():
    required = [
        "docs/M49_EXECUTION_BACKLOG.md",
        "docs/desktop/seat_input_contract_v1.md",
        "docs/desktop/input_event_contract_v1.md",
        "docs/desktop/focus_routing_policy_v1.md",
        "tests/desktop/test_input_seat_docs_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M49 PR-1 artifact: {rel}"


def test_seat_input_contract_v1_doc_declares_required_tokens():
    doc = _read("docs/desktop/seat_input_contract_v1.md")
    for token in [
        "Seat input contract ID: `rugo.seat_input_contract.v1`.",
        "Parent display runtime contract ID: `rugo.display_runtime_contract.v1`.",
        "Parent input stack contract ID: `rugo.input_stack_contract.v1`.",
        "Runtime report schema: `rugo.input_seat_runtime_report.v1`.",
        "HID event-path schema: `rugo.hid_event_path_report.v1`.",
        "`seat0`",
        "`usb-hid`",
        "`xhci-usb-hid`",
        "`keyboard_event_delivery`",
        "`seat_hotplug_rebind`",
        "Local gate: `make test-input-seat-v1`.",
        "Local sub-gate: `make test-hid-event-path-v1`.",
        "CI gate: `Input seat v1 gate`.",
        "CI sub-gate: `HID event path v1 gate`.",
    ]:
        assert token in doc


def test_input_event_contract_v1_doc_declares_required_tokens():
    doc = _read("docs/desktop/input_event_contract_v1.md")
    for token in [
        "Input event contract ID: `rugo.input_event_contract.v1`.",
        "Parent seat contract ID: `rugo.seat_input_contract.v1`.",
        "Runtime report schema: `rugo.input_seat_runtime_report.v1`.",
        "HID event-path schema: `rugo.hid_event_path_report.v1`.",
        "Required keyboard phases: `key_down`, `key_repeat`, `key_up`.",
        "Required pointer phases: `pointer_motion`, `button_down`, `button_up`.",
        "`event_sequence_integrity`",
        "`pointer_button_delivery`",
    ]:
        assert token in doc


def test_focus_routing_policy_v1_doc_declares_required_tokens():
    doc = _read("docs/desktop/focus_routing_policy_v1.md")
    for token in [
        "Focus routing policy ID: `rugo.focus_routing_policy.v1`.",
        "Parent seat contract ID: `rugo.seat_input_contract.v1`.",
        "Runtime report schema: `rugo.input_seat_runtime_report.v1`.",
        "Keyboard delivery follows the logical focus owner.",
        "Pointer delivery follows the hit-tested surface unless capture is active.",
        "`focus_route_integrity` must remain `0` misroutes.",
        "`focus_transition_budget` must remain `<= 35 ms`.",
        "Only one focus owner may exist per seat.",
    ]:
        assert token in doc


def test_m49_roadmap_anchor_declares_input_seat_gates():
    roadmap = _read("docs/M48_M52_GUI_IMPLEMENTATION_ROADMAP.md")
    assert "test-input-seat-v1" in roadmap
    assert "test-hid-event-path-v1" in roadmap
