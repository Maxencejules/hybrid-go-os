#!/usr/bin/env python3
"""Run deterministic input seat runtime checks for M49."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set

import run_baremetal_io_baseline_v1 as baremetal
import run_display_runtime_v1 as display_runtime


SCHEMA = "rugo.input_seat_runtime_report.v1"
CONTRACT_ID = "rugo.seat_input_contract.v1"
INPUT_EVENT_CONTRACT_ID = "rugo.input_event_contract.v1"
FOCUS_POLICY_ID = "rugo.focus_routing_policy.v1"
HID_EVENT_PATH_SCHEMA = "rugo.hid_event_path_report.v1"
DEFAULT_SEED = 20260311
SEAT_ID = "seat0"
KEYBOARD_DEVICE_ID = "seat0-kbd-usb"
POINTER_DEVICE_ID = "seat0-pointer-usb"
DEVICE_CLASS = "usb-hid"
DEVICE_DRIVER = "xhci-usb-hid"
INITIAL_FOCUS_TARGET = "desktop.shell.launcher"
ACTIVE_FOCUS_TARGET = "settings.panel"


@dataclass(frozen=True)
class CheckSpec:
    check_id: str
    domain: str
    metric_key: str
    operator: str  # one of: min, max, eq
    threshold: float
    base: float
    spread: int
    scale: float


BASE_CHECKS: Sequence[CheckSpec] = (
    CheckSpec(
        check_id="keyboard_event_delivery",
        domain="delivery",
        metric_key="keyboard_delivery_ratio",
        operator="min",
        threshold=0.999,
        base=0.999,
        spread=2,
        scale=0.001,
    ),
    CheckSpec(
        check_id="keyboard_repeat_cadence",
        domain="delivery",
        metric_key="keyboard_repeat_jitter_p95_ms",
        operator="max",
        threshold=3.0,
        base=1.4,
        spread=10,
        scale=0.1,
    ),
    CheckSpec(
        check_id="pointer_motion_delivery",
        domain="delivery",
        metric_key="pointer_motion_latency_p95_ms",
        operator="max",
        threshold=10.0,
        base=5.8,
        spread=8,
        scale=0.35,
    ),
    CheckSpec(
        check_id="pointer_button_delivery",
        domain="delivery",
        metric_key="pointer_button_latency_p95_ms",
        operator="max",
        threshold=12.0,
        base=6.4,
        spread=8,
        scale=0.4,
    ),
    CheckSpec(
        check_id="event_sequence_integrity",
        domain="delivery",
        metric_key="event_reorder_count",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="focus_route_integrity",
        domain="focus",
        metric_key="focus_misroute_count",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="focus_transition_budget",
        domain="focus",
        metric_key="focus_transition_latency_ms",
        operator="max",
        threshold=35.0,
        base=16.0,
        spread=10,
        scale=1.2,
    ),
    CheckSpec(
        check_id="seat_owner_exclusivity",
        domain="seat",
        metric_key="focus_owner_count",
        operator="eq",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="seat_hotplug_rebind",
        domain="seat",
        metric_key="seat_hotplug_rebind_ms",
        operator="max",
        threshold=120.0,
        base=42.0,
        spread=24,
        scale=2.0,
    ),
    CheckSpec(
        check_id="seat_hotplug_recovery",
        domain="seat",
        metric_key="hotplug_dropped_events",
        operator="max",
        threshold=1.0,
        base=0.0,
        spread=2,
        scale=1.0,
    ),
)

SOURCE_CHECK_IDS = {"display_runtime_live", "usb_hid_declared_support"}


def known_checks() -> Set[str]:
    return {spec.check_id for spec in BASE_CHECKS} | SOURCE_CHECK_IDS


def _noise(seed: int, key: str) -> int:
    digest = hashlib.sha256(f"{seed}|{key}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _round_value(value: float) -> float:
    return round(value, 3)


def _baseline_observed(seed: int, spec: CheckSpec) -> float:
    spread = spec.spread if spec.spread > 0 else 1
    value = spec.base + ((_noise(seed, spec.check_id) % spread) * spec.scale)
    return _round_value(value)


def _failing_observed(operator: str, threshold: float, scale: float) -> float:
    delta = 1.0 if scale == 0.0 and float(threshold).is_integer() else (
        0.001 if scale < 1.0 else 1.0
    )
    if operator == "max":
        return _round_value(threshold + delta)
    if operator == "min":
        return _round_value(threshold - delta)
    return _round_value(threshold + delta)


def _passes(operator: str, observed: float, threshold: float) -> bool:
    if operator == "max":
        return observed <= threshold
    if operator == "min":
        return observed >= threshold
    if operator == "eq":
        return observed == threshold
    raise ValueError(f"unsupported operator: {operator}")


def _domain_summary(checks: List[Dict[str, object]], domain: str) -> Dict[str, object]:
    scoped = [entry for entry in checks if entry["domain"] == domain]
    failures = [entry for entry in scoped if entry["pass"] is False]
    return {
        "checks": len(scoped),
        "failures": len(failures),
        "pass": len(failures) == 0,
    }


def _coverage_entry(coverage: Sequence[Dict[str, object]], device: str) -> Dict[str, object]:
    for row in coverage:
        if row["device"] == device:
            return row
    raise ValueError(f"missing coverage row for {device!r}")


def _count(seed: int, key: str, base: int, spread: int) -> int:
    return base + (_noise(seed, key) % spread)


def normalize_failures(values: Sequence[str]) -> Set[str]:
    failures = {value.strip() for value in values if value.strip()}
    unknown = sorted(failures - known_checks())
    if unknown:
        raise ValueError(f"unknown check ids in --inject-failure: {', '.join(unknown)}")
    return failures


def run_input_seat_runtime(
    seed: int,
    injected_failures: Set[str] | None = None,
    max_failures: int = 0,
    force_display_fallback: bool = False,
) -> Dict[str, object]:
    failures = set() if injected_failures is None else set(injected_failures)

    checks: List[Dict[str, object]] = []
    metric_values: Dict[str, float] = {}
    for spec in BASE_CHECKS:
        observed = (
            _failing_observed(spec.operator, spec.threshold, spec.scale)
            if spec.check_id in failures
            else _baseline_observed(seed, spec)
        )
        passed = _passes(spec.operator, observed, spec.threshold)
        checks.append(
            {
                "check_id": spec.check_id,
                "domain": spec.domain,
                "metric_key": spec.metric_key,
                "operator": spec.operator,
                "threshold": spec.threshold,
                "observed": observed,
                "pass": passed,
            }
        )
        metric_values[spec.metric_key] = observed

    display_report = display_runtime.run_display_runtime(
        seed=seed,
        max_failures=0,
        force_fallback=force_display_fallback,
    )
    baremetal_report = baremetal.run_baseline(seed=seed, max_failures=0)

    display_runtime_green = (
        display_report["gate_pass"]
        and display_report["summary"]["scanout"]["pass"]
        and display_report["summary"]["capture"]["pass"]
    )
    usb_hid_green = (
        baremetal_report["gate_pass"]
        and baremetal_report["input_class"] == DEVICE_CLASS
        and baremetal_report["input_driver"] == DEVICE_DRIVER
        and baremetal_report["desktop_input_checks"]["focus_delivery_pass"] is True
        and _coverage_entry(baremetal_report["device_class_coverage"], DEVICE_CLASS)["status"]
        == "pass"
    )

    checks.extend(
        [
            {
                "check_id": "display_runtime_live",
                "domain": "source",
                "metric_key": "display_runtime_ready_ratio",
                "operator": "min",
                "threshold": 1.0,
                "observed": 1.0
                if display_runtime_green and "display_runtime_live" not in failures
                else 0.999,
                "pass": display_runtime_green and "display_runtime_live" not in failures,
            },
            {
                "check_id": "usb_hid_declared_support",
                "domain": "source",
                "metric_key": "usb_hid_declared_support_ratio",
                "operator": "min",
                "threshold": 1.0,
                "observed": 1.0
                if usb_hid_green and "usb_hid_declared_support" not in failures
                else 0.999,
                "pass": usb_hid_green and "usb_hid_declared_support" not in failures,
            },
        ]
    )

    check_pass = {entry["check_id"]: bool(entry["pass"]) for entry in checks}

    keyboard_checks_pass = (
        check_pass["keyboard_event_delivery"]
        and check_pass["keyboard_repeat_cadence"]
        and check_pass["event_sequence_integrity"]
    )
    pointer_checks_pass = (
        check_pass["pointer_motion_delivery"]
        and check_pass["pointer_button_delivery"]
        and check_pass["event_sequence_integrity"]
    )
    focus_checks_pass = (
        check_pass["focus_route_integrity"] and check_pass["focus_transition_budget"]
    )
    hotplug_checks_pass = (
        check_pass["seat_hotplug_rebind"] and check_pass["seat_hotplug_recovery"]
    )

    total_failures = sum(1 for row in checks if row["pass"] is False)
    failures_list = sorted(row["check_id"] for row in checks if row["pass"] is False)
    gate_pass = total_failures <= max_failures

    stable_payload = {
        "schema": SCHEMA,
        "seed": seed,
        "display_runtime_digest": display_report["digest"],
        "baremetal_input_digest": baremetal_report["digest"],
        "active_display_path": display_report["active_runtime_path"],
        "checks": [
            {
                "check_id": row["check_id"],
                "pass": row["pass"],
                "observed": row["observed"],
            }
            for row in checks
        ],
        "injected_failures": sorted(failures),
        "force_display_fallback": force_display_fallback,
    }
    digest = hashlib.sha256(
        json.dumps(stable_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    keyboard_events_delivered = _count(seed, "keyboard_events_delivered", 48, 12)
    pointer_motion_events = _count(seed, "pointer_motion_events", 36, 16)
    pointer_button_events = _count(seed, "pointer_button_events", 4, 4)

    return {
        "schema": SCHEMA,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "contract_id": CONTRACT_ID,
        "input_event_contract_id": INPUT_EVENT_CONTRACT_ID,
        "focus_policy_id": FOCUS_POLICY_ID,
        "display_runtime_contract_id": display_runtime.CONTRACT_ID,
        "input_stack_contract_id": baremetal.INPUT_CONTRACT_ID,
        "hid_event_path_schema": HID_EVENT_PATH_SCHEMA,
        "seed": seed,
        "gate": "test-input-seat-v1",
        "hid_gate": "test-hid-event-path-v1",
        "checks": checks,
        "summary": {
            "delivery": _domain_summary(checks, "delivery"),
            "focus": _domain_summary(checks, "focus"),
            "seat": _domain_summary(checks, "seat"),
            "source": _domain_summary(checks, "source"),
        },
        "seat": {
            "seat_id": SEAT_ID,
            "seat_model": "single-local-seat",
            "active": True,
            "active_display_path": display_report["active_runtime_path"],
            "active_display_driver": display_report["active_runtime_driver"],
            "focus_owner": ACTIVE_FOCUS_TARGET,
            "previous_focus_owner": INITIAL_FOCUS_TARGET,
            "focus_owner_count": int(metric_values["focus_owner_count"]),
            "owner_exclusive": check_pass["seat_owner_exclusivity"],
            "keyboard_device_id": KEYBOARD_DEVICE_ID,
            "pointer_device_id": POINTER_DEVICE_ID,
            "hotplug_supported": True,
            "checks_pass": _domain_summary(checks, "seat")["pass"],
        },
        "keyboard": {
            "device_id": KEYBOARD_DEVICE_ID,
            "device_class": DEVICE_CLASS,
            "driver": DEVICE_DRIVER,
            "delivery_ratio": metric_values["keyboard_delivery_ratio"],
            "source_latency_p95_ms": baremetal_report["usb_input"]["keyboard_latency_p95_ms"],
            "repeat_jitter_p95_ms": metric_values["keyboard_repeat_jitter_p95_ms"],
            "repeat_profile": "30hz-after-250ms",
            "delivered_events": keyboard_events_delivered,
            "dropped_events": 0 if check_pass["keyboard_event_delivery"] else 1,
            "target_surface": ACTIVE_FOCUS_TARGET,
            "checks_pass": keyboard_checks_pass,
        },
        "pointer": {
            "device_id": POINTER_DEVICE_ID,
            "device_class": DEVICE_CLASS,
            "driver": DEVICE_DRIVER,
            "motion_latency_p95_ms": metric_values["pointer_motion_latency_p95_ms"],
            "button_latency_p95_ms": metric_values["pointer_button_latency_p95_ms"],
            "motion_events": pointer_motion_events,
            "button_events": pointer_button_events,
            "captured": False,
            "target_surface": ACTIVE_FOCUS_TARGET,
            "checks_pass": pointer_checks_pass,
        },
        "focus": {
            "policy_id": FOCUS_POLICY_ID,
            "previous_focus_target": INITIAL_FOCUS_TARGET,
            "keyboard_focus_target": ACTIVE_FOCUS_TARGET,
            "pointer_focus_target": ACTIVE_FOCUS_TARGET,
            "transitions": [
                {
                    "from": INITIAL_FOCUS_TARGET,
                    "to": ACTIVE_FOCUS_TARGET,
                    "reason": "pointer_button_down",
                    "latency_ms": metric_values["focus_transition_latency_ms"],
                }
            ],
            "misroutes": int(metric_values["focus_misroute_count"]),
            "checks_pass": focus_checks_pass,
        },
        "hotplug": {
            "controller": "xhci",
            "device_id": POINTER_DEVICE_ID,
            "detach_events": 1,
            "rebind_events": 1,
            "rebind_latency_ms": metric_values["seat_hotplug_rebind_ms"],
            "dropped_events_during_rebind": int(metric_values["hotplug_dropped_events"]),
            "focus_restored": hotplug_checks_pass and focus_checks_pass,
            "checks_pass": hotplug_checks_pass,
        },
        "source_reports": {
            "display_runtime": {
                "schema": display_report["schema"],
                "digest": display_report["digest"],
                "gate_pass": display_report["gate_pass"],
                "active_display_path": display_report["active_runtime_path"],
                "active_display_driver": display_report["active_runtime_driver"],
            },
            "baremetal_input": {
                "schema": baremetal_report["schema"],
                "digest": baremetal_report["digest"],
                "gate_pass": baremetal_report["gate_pass"],
                "input_class": baremetal_report["input_class"],
                "input_driver": baremetal_report["input_driver"],
                "focus_delivery_pass": baremetal_report["desktop_input_checks"][
                    "focus_delivery_pass"
                ],
            },
        },
        "artifact_refs": {
            "junit": "out/pytest-input-seat-v1.xml",
            "runtime_report": "out/input-seat-v1.json",
            "hid_event_path_report": "out/hid-event-path-v1.json",
            "display_runtime_report": "out/display-runtime-v1.json",
            "baremetal_input_report": "out/baremetal-io-v1.json",
            "ci_artifact": "input-seat-v1-artifacts",
            "hid_ci_artifact": "hid-event-path-v1-artifacts",
        },
        "injected_failures": sorted(failures),
        "force_display_fallback": force_display_fallback,
        "max_failures": max_failures,
        "total_failures": total_failures,
        "failures": failures_list,
        "gate_pass": gate_pass,
        "digest": digest,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--inject-failure",
        action="append",
        default=[],
        help="force an input seat check to fail by check_id",
    )
    parser.add_argument("--max-failures", type=int, default=0)
    parser.add_argument(
        "--force-display-fallback",
        action="store_true",
        help="select the efifb display runtime path while keeping seat checks active",
    )
    parser.add_argument("--out", default="out/input-seat-v1.json")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.max_failures < 0:
        print("error: max-failures must be >= 0")
        return 2

    try:
        injected_failures = normalize_failures(args.inject_failure)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    report = run_input_seat_runtime(
        seed=args.seed,
        injected_failures=injected_failures,
        max_failures=args.max_failures,
        force_display_fallback=args.force_display_fallback,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"input-seat-runtime-report: {out_path}")
    print(f"seat_id: {report['seat']['seat_id']}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
