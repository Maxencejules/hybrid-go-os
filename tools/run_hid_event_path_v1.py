#!/usr/bin/env python3
"""Run deterministic HID event-path checks for M49."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence

import run_input_seat_runtime_v1 as runtime


SCHEMA = runtime.HID_EVENT_PATH_SCHEMA
DEFAULT_SEED = runtime.DEFAULT_SEED


def _noise(seed: int, key: str) -> int:
    digest = hashlib.sha256(f"{seed}|{key}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _event_stream(seed: int, runtime_report: Dict[str, object]) -> List[Dict[str, object]]:
    pointer_x = 96 + (_noise(seed, "pointer_x") % 48)
    pointer_y = 54 + (_noise(seed, "pointer_y") % 36)
    return [
        {
            "seq": 1,
            "seat_id": runtime.SEAT_ID,
            "device_id": runtime.POINTER_DEVICE_ID,
            "device": "pointer",
            "phase": "pointer_motion",
            "target": runtime.INITIAL_FOCUS_TARGET,
            "x": pointer_x,
            "y": pointer_y,
            "focus_before": runtime.INITIAL_FOCUS_TARGET,
            "focus_after": runtime.INITIAL_FOCUS_TARGET,
        },
        {
            "seq": 2,
            "seat_id": runtime.SEAT_ID,
            "device_id": runtime.POINTER_DEVICE_ID,
            "device": "pointer",
            "phase": "button_down",
            "button": "BTN_LEFT",
            "target": runtime.ACTIVE_FOCUS_TARGET,
            "focus_before": runtime.INITIAL_FOCUS_TARGET,
            "focus_after": runtime.ACTIVE_FOCUS_TARGET,
        },
        {
            "seq": 3,
            "seat_id": runtime.SEAT_ID,
            "device_id": runtime.POINTER_DEVICE_ID,
            "device": "pointer",
            "phase": "button_up",
            "button": "BTN_LEFT",
            "target": runtime.ACTIVE_FOCUS_TARGET,
            "focus_before": runtime.ACTIVE_FOCUS_TARGET,
            "focus_after": runtime.ACTIVE_FOCUS_TARGET,
        },
        {
            "seq": 4,
            "seat_id": runtime.SEAT_ID,
            "device_id": runtime.KEYBOARD_DEVICE_ID,
            "device": "keyboard",
            "phase": "key_down",
            "code": "KEY_DOWN",
            "target": runtime.ACTIVE_FOCUS_TARGET,
            "focus_owner": runtime.ACTIVE_FOCUS_TARGET,
        },
        {
            "seq": 5,
            "seat_id": runtime.SEAT_ID,
            "device_id": runtime.KEYBOARD_DEVICE_ID,
            "device": "keyboard",
            "phase": "key_repeat",
            "code": "KEY_DOWN",
            "target": runtime.ACTIVE_FOCUS_TARGET,
            "focus_owner": runtime.ACTIVE_FOCUS_TARGET,
        },
        {
            "seq": 6,
            "seat_id": runtime.SEAT_ID,
            "device_id": runtime.KEYBOARD_DEVICE_ID,
            "device": "keyboard",
            "phase": "key_up",
            "code": "KEY_DOWN",
            "target": runtime.ACTIVE_FOCUS_TARGET,
            "focus_owner": runtime.ACTIVE_FOCUS_TARGET,
        },
        {
            "seq": 7,
            "seat_id": runtime.SEAT_ID,
            "device_id": runtime.POINTER_DEVICE_ID,
            "device": "hotplug",
            "phase": "device_detach",
            "target": runtime.SEAT_ID,
            "focus_owner": runtime.ACTIVE_FOCUS_TARGET,
        },
        {
            "seq": 8,
            "seat_id": runtime.SEAT_ID,
            "device_id": runtime.POINTER_DEVICE_ID,
            "device": "hotplug",
            "phase": "device_rebind",
            "target": runtime.ACTIVE_FOCUS_TARGET,
            "focus_owner": runtime.ACTIVE_FOCUS_TARGET,
            "latency_ms": runtime_report["hotplug"]["rebind_latency_ms"],
        },
    ]


def run_hid_event_path(
    seed: int,
    runtime_failures: Sequence[str] | None = None,
    force_display_fallback: bool = False,
) -> Dict[str, object]:
    runtime_report = runtime.run_input_seat_runtime(
        seed=seed,
        injected_failures=set(runtime_failures or []),
        max_failures=0,
        force_display_fallback=force_display_fallback,
    )

    events = _event_stream(seed, runtime_report)
    phases = [event["phase"] for event in events]
    required_keyboard_phases = ["key_down", "key_repeat", "key_up"]
    required_pointer_phases = ["pointer_motion", "button_down", "button_up"]
    keyboard_phase_pass = all(phase in phases for phase in required_keyboard_phases)
    pointer_phase_pass = all(phase in phases for phase in required_pointer_phases)
    hotplug_phase_pass = "device_detach" in phases and "device_rebind" in phases
    ordered = phases == [event["phase"] for event in sorted(events, key=lambda row: row["seq"])]

    stable_payload = {
        "schema": SCHEMA,
        "runtime_digest": runtime_report["digest"],
        "event_stream": events,
        "force_display_fallback": force_display_fallback,
    }
    sequence_sha256 = hashlib.sha256(
        json.dumps(stable_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    path_checks_pass = (
        runtime_report["gate_pass"]
        and runtime_report["keyboard"]["checks_pass"]
        and runtime_report["pointer"]["checks_pass"]
        and runtime_report["focus"]["checks_pass"]
        and runtime_report["hotplug"]["checks_pass"]
        and keyboard_phase_pass
        and pointer_phase_pass
        and hotplug_phase_pass
        and ordered
    )

    return {
        "schema": SCHEMA,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "runtime_schema": runtime_report["schema"],
        "runtime_digest": runtime_report["digest"],
        "runtime_gate_pass": runtime_report["gate_pass"],
        "seat_contract_id": runtime_report["contract_id"],
        "input_event_contract_id": runtime_report["input_event_contract_id"],
        "focus_policy_id": runtime_report["focus_policy_id"],
        "seat_id": runtime_report["seat"]["seat_id"],
        "active_display_path": runtime_report["seat"]["active_display_path"],
        "keyboard_device_id": runtime_report["keyboard"]["device_id"],
        "pointer_device_id": runtime_report["pointer"]["device_id"],
        "focus_target": runtime_report["focus"]["keyboard_focus_target"],
        "required_keyboard_phases": required_keyboard_phases,
        "required_pointer_phases": required_pointer_phases,
        "event_stream": events,
        "event_counts": {
            "total": len(events),
            "keyboard": sum(1 for event in events if event["device"] == "keyboard"),
            "pointer": sum(1 for event in events if event["device"] == "pointer"),
            "hotplug": sum(1 for event in events if event["device"] == "hotplug"),
        },
        "keyboard_path": {
            "target": runtime_report["keyboard"]["target_surface"],
            "delivery_ratio": runtime_report["keyboard"]["delivery_ratio"],
            "repeat_jitter_p95_ms": runtime_report["keyboard"]["repeat_jitter_p95_ms"],
            "phases_present": keyboard_phase_pass,
            "path_checks_pass": runtime_report["keyboard"]["checks_pass"]
            and keyboard_phase_pass
            and runtime_report["focus"]["checks_pass"],
        },
        "pointer_path": {
            "target": runtime_report["pointer"]["target_surface"],
            "motion_latency_p95_ms": runtime_report["pointer"]["motion_latency_p95_ms"],
            "button_latency_p95_ms": runtime_report["pointer"]["button_latency_p95_ms"],
            "phases_present": pointer_phase_pass,
            "path_checks_pass": runtime_report["pointer"]["checks_pass"]
            and pointer_phase_pass
            and runtime_report["focus"]["checks_pass"],
        },
        "focus_path": {
            "previous_focus_target": runtime_report["focus"]["previous_focus_target"],
            "active_focus_target": runtime_report["focus"]["keyboard_focus_target"],
            "transition_latency_ms": runtime_report["focus"]["transitions"][0]["latency_ms"],
            "misroutes": runtime_report["focus"]["misroutes"],
            "path_checks_pass": runtime_report["focus"]["checks_pass"],
        },
        "hotplug_path": {
            "device_id": runtime_report["hotplug"]["device_id"],
            "rebind_latency_ms": runtime_report["hotplug"]["rebind_latency_ms"],
            "dropped_events_during_rebind": runtime_report["hotplug"][
                "dropped_events_during_rebind"
            ],
            "detach_and_rebind_present": hotplug_phase_pass,
            "path_checks_pass": runtime_report["hotplug"]["checks_pass"]
            and hotplug_phase_pass,
        },
        "sequence_sha256": sequence_sha256,
        "runtime_failures": runtime_report["failures"],
        "force_display_fallback": force_display_fallback,
        "path_checks_pass": path_checks_pass,
        "gate_pass": path_checks_pass,
        "artifact_refs": {
            "json_path": "out/hid-event-path-v1.json",
            "runtime_report": runtime_report["artifact_refs"]["runtime_report"],
            "junit": "out/pytest-hid-event-path-v1.xml",
        },
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--inject-runtime-failure",
        action="append",
        default=[],
        help="force an input seat runtime check to fail before building the HID path",
    )
    parser.add_argument(
        "--force-display-fallback",
        action="store_true",
        help="select the efifb display runtime path while keeping event-path checks active",
    )
    parser.add_argument("--out", default="out/hid-event-path-v1.json")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        runtime_failures = runtime.normalize_failures(args.inject_runtime_failure)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    report = run_hid_event_path(
        seed=args.seed,
        runtime_failures=sorted(runtime_failures),
        force_display_fallback=args.force_display_fallback,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"hid-event-path-report: {out_path}")
    print(f"seat_id: {report['seat_id']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
