#!/usr/bin/env python3
"""Run deterministic toolkit compatibility checks for M51."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set

import run_gui_runtime_v1 as runtime


SCHEMA = "rugo.toolkit_compat_report.v1"
PROFILE_ID = "rugo.toolkit_profile.v1"
FONT_POLICY_ID = "rugo.font_text_rendering_policy.v1"
DEFAULT_SEED = 20260311


@dataclass(frozen=True)
class ProfileThreshold:
    min_cases: int
    min_pass_rate: float
    render_model: str
    event_model: str
    text_backend: str


PROFILE_THRESHOLDS: Dict[str, ProfileThreshold] = {
    runtime.RETAIN_PROFILE: ProfileThreshold(
        min_cases=3,
        min_pass_rate=1.0,
        render_model="retained-scene",
        event_model="single-ui-thread-plus-runtime-queue",
        text_backend="atlas-text",
    ),
    runtime.OVERLAY_PROFILE: ProfileThreshold(
        min_cases=1,
        min_pass_rate=1.0,
        render_model="immediate-overlay",
        event_model="timer-plus-paint",
        text_backend="atlas-text",
    ),
}


def _known_case_ids() -> Set[str]:
    return {spec.app_id for spec in runtime.APP_SPECS}


def _normalize_case_ids(values: Sequence[str]) -> Set[str]:
    return {value.strip() for value in values if value.strip()}


def _validate_case_ids(label: str, case_ids: Set[str]) -> None:
    unknown = sorted(case_ids - _known_case_ids())
    if unknown:
        raise ValueError(f"unknown case ids in {label}: {', '.join(unknown)}")


def _noise(seed: int, key: str) -> int:
    digest = hashlib.sha256(f"{seed}|{key}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _metric(seed: int, key: str, label: str, base: float, spread: int, scale: float) -> float:
    return round(base + ((_noise(seed, f"{key}|{label}") % spread) * scale), 3)


def _build_cases(
    runtime_report: Dict[str, object],
    launch_failures: Set[str],
    render_failures: Set[str],
    input_failures: Set[str],
    text_failures: Set[str],
    event_loop_failures: Set[str],
    nondeterministic: Set[str],
    profile_mismatches: Set[str],
) -> List[Dict[str, object]]:
    cases: List[Dict[str, object]] = []
    for app in runtime_report["apps"]:
        profile = app["toolkit_profile"]
        if app["app_id"] in profile_mismatches:
            profile = "rugo.widgets.unknown.v0"

        cases.append(
            {
                "case_id": app["app_id"],
                "window_id": app["window_id"],
                "expected_profile": app["toolkit_profile"],
                "profile": profile,
                "input_required": app["input_required"],
                "launch_ok": app["launch_ok"] and app["app_id"] not in launch_failures,
                "render_ok": app["render_ok"] and app["app_id"] not in render_failures,
                "input_ok": app["input_ok"] and app["app_id"] not in input_failures,
                "text_ok": app["text_ok"] and app["app_id"] not in text_failures,
                "event_loop_ok": (
                    app["event_loop_ok"] and app["app_id"] not in event_loop_failures
                ),
                "deterministic": app["app_id"] not in nondeterministic,
                "retired": app["retired"],
                "metrics": {
                    "launch_ms": app["launch_ms"],
                    "first_frame_ms": app["first_frame_ms"],
                    "frame_latency_p95_ms": app["frame_latency_p95_ms"],
                    "input_latency_p95_ms": app["input_latency_p95_ms"],
                },
            }
        )
    return cases


def run_toolkit_compat(
    seed: int,
    launch_failures: Set[str] | None = None,
    render_failures: Set[str] | None = None,
    input_failures: Set[str] | None = None,
    text_failures: Set[str] | None = None,
    event_loop_failures: Set[str] | None = None,
    nondeterministic: Set[str] | None = None,
    profile_mismatches: Set[str] | None = None,
    max_failures: int = 0,
    force_display_fallback: bool = False,
) -> Dict[str, object]:
    launch = set() if launch_failures is None else set(launch_failures)
    render = set() if render_failures is None else set(render_failures)
    inputf = set() if input_failures is None else set(input_failures)
    textf = set() if text_failures is None else set(text_failures)
    eventf = set() if event_loop_failures is None else set(event_loop_failures)
    nondet = set() if nondeterministic is None else set(nondeterministic)
    profile_bad = set() if profile_mismatches is None else set(profile_mismatches)

    runtime_report = runtime.run_gui_runtime(
        seed=seed,
        max_failures=0,
        force_display_fallback=force_display_fallback,
    )
    runtime_source_ready = runtime_report["gate_pass"]

    cases = _build_cases(
        runtime_report,
        launch_failures=launch,
        render_failures=render,
        input_failures=inputf,
        text_failures=textf,
        event_loop_failures=eventf,
        nondeterministic=nondet,
        profile_mismatches=profile_bad,
    )

    profile_totals = {
        profile_id: {"eligible": 0, "passed": 0}
        for profile_id in sorted(PROFILE_THRESHOLDS.keys())
    }
    issues: List[Dict[str, object]] = []
    case_reports: List[Dict[str, object]] = []

    for case in sorted(cases, key=lambda item: item["case_id"]):
        expected = PROFILE_THRESHOLDS.get(case["profile"])
        counted_for_threshold = True
        if expected is None:
            issues.append({"case_id": case["case_id"], "reason": "profile_mismatch"})
            counted_for_threshold = False
        elif case["profile"] != case["expected_profile"]:
            issues.append({"case_id": case["case_id"], "reason": "profile_mismatch"})
            counted_for_threshold = False
        elif not case["deterministic"]:
            issues.append({"case_id": case["case_id"], "reason": "non_deterministic_result"})
            counted_for_threshold = False
        elif not runtime_source_ready:
            issues.append({"case_id": case["case_id"], "reason": "runtime_source_failed"})
            counted_for_threshold = False

        passed = (
            case["launch_ok"]
            and case["render_ok"]
            and case["text_ok"]
            and case["event_loop_ok"]
            and (not case["input_required"] or case["input_ok"])
        )

        if counted_for_threshold:
            bucket = profile_totals[case["profile"]]
            bucket["eligible"] += 1
            if passed:
                bucket["passed"] += 1

        if counted_for_threshold and not case["launch_ok"]:
            issues.append({"case_id": case["case_id"], "reason": "launch_failure"})
        if counted_for_threshold and not case["render_ok"]:
            issues.append({"case_id": case["case_id"], "reason": "render_failure"})
        if counted_for_threshold and case["input_required"] and not case["input_ok"]:
            issues.append({"case_id": case["case_id"], "reason": "input_failure"})
        if counted_for_threshold and not case["text_ok"]:
            issues.append({"case_id": case["case_id"], "reason": "text_failure"})
        if counted_for_threshold and not case["event_loop_ok"]:
            issues.append({"case_id": case["case_id"], "reason": "event_loop_failure"})

        case_reports.append(
            {
                "case_id": case["case_id"],
                "window_id": case["window_id"],
                "profile": case["profile"],
                "expected_profile": case["expected_profile"],
                "launch_ok": case["launch_ok"],
                "render_ok": case["render_ok"],
                "input_required": case["input_required"],
                "input_ok": case["input_ok"],
                "text_ok": case["text_ok"],
                "event_loop_ok": case["event_loop_ok"],
                "deterministic": case["deterministic"],
                "retired": case["retired"],
                "counted_for_threshold": counted_for_threshold,
                "passed": passed,
                "metrics": case["metrics"],
            }
        )

    profile_reports: Dict[str, Dict[str, object]] = {}
    profile_failures = 0
    for profile_id in sorted(PROFILE_THRESHOLDS.keys()):
        threshold = PROFILE_THRESHOLDS[profile_id]
        stats = profile_totals[profile_id]
        eligible = int(stats["eligible"])
        passed = int(stats["passed"])
        pass_rate = (passed / eligible) if eligible else 0.0
        meets_threshold = (
            eligible >= threshold.min_cases and pass_rate >= threshold.min_pass_rate
        )
        if not meets_threshold:
            profile_failures += 1

        profile_reports[profile_id] = {
            "render_model": threshold.render_model,
            "event_model": threshold.event_model,
            "text_backend": threshold.text_backend,
            "eligible": eligible,
            "passed": passed,
            "pass_rate": pass_rate,
            "min_cases": threshold.min_cases,
            "min_pass_rate": threshold.min_pass_rate,
            "meets_threshold": meets_threshold,
        }

    issues_sorted = sorted(issues, key=lambda item: (str(item["reason"]), item["case_id"]))
    total_failures = len(issues_sorted) + profile_failures
    gate_pass = total_failures <= max_failures

    stable_payload = {
        "schema": SCHEMA,
        "profile_id": PROFILE_ID,
        "runtime_digest": runtime_report["digest"],
        "seed": seed,
        "profiles": {
            key: {
                "eligible": value["eligible"],
                "passed": value["passed"],
                "meets_threshold": value["meets_threshold"],
            }
            for key, value in profile_reports.items()
        },
        "cases": [
            {
                "case_id": item["case_id"],
                "profile": item["profile"],
                "passed": item["passed"],
                "counted_for_threshold": item["counted_for_threshold"],
            }
            for item in case_reports
        ],
        "issues": issues_sorted,
    }
    digest = hashlib.sha256(
        json.dumps(stable_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return {
        "schema": SCHEMA,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "profile_id": PROFILE_ID,
        "gui_runtime_contract_id": runtime.CONTRACT_ID,
        "runtime_schema": runtime.SCHEMA,
        "font_policy_id": FONT_POLICY_ID,
        "seed": seed,
        "gate": "test-toolkit-compat-v1",
        "parent_gate": "test-gui-runtime-v1",
        "profiles": profile_reports,
        "cases": case_reports,
        "issues": issues_sorted,
        "event_loop_profiles": {
            runtime.RETAIN_PROFILE: {
                "dispatch_model": runtime_report["event_loop"]["dispatch_model"],
                "callback_order": runtime_report["event_loop"]["callback_order"],
                "wakeup_latency_p95_ms": runtime_report["event_loop"][
                    "wakeup_latency_p95_ms"
                ],
                "queue_drain_latency_p95_ms": runtime_report["event_loop"][
                    "queue_drain_latency_p95_ms"
                ],
            },
            runtime.OVERLAY_PROFILE: {
                "dispatch_model": "timer-plus-paint",
                "callback_order": ["timer", "paint", "present"],
                "wakeup_latency_p95_ms": _metric(
                    seed, runtime.OVERLAY_PROFILE, "wakeup", base=2.4, spread=5, scale=0.2
                ),
                "queue_drain_latency_p95_ms": _metric(
                    seed, runtime.OVERLAY_PROFILE, "queue", base=3.0, spread=5, scale=0.25
                ),
            },
        },
        "source_reports": {
            "gui_runtime": {
                "schema": runtime_report["schema"],
                "digest": runtime_report["digest"],
                "gate_pass": runtime_report["gate_pass"],
                "focus_owner": runtime_report["runtime_topology"]["focus_owner"],
                "active_display_path": runtime_report["runtime_topology"][
                    "active_display_path"
                ],
            }
        },
        "artifact_refs": {
            "junit": "out/pytest-toolkit-compat-v1.xml",
            "compat_report": "out/toolkit-compat-v1.json",
            "runtime_report": "out/gui-runtime-v1.json",
            "ci_artifact": "toolkit-compat-v1-artifacts",
            "runtime_ci_artifact": "gui-runtime-v1-artifacts",
        },
        "injected_launch_failures": sorted(launch),
        "injected_render_failures": sorted(render),
        "injected_input_failures": sorted(inputf),
        "injected_text_failures": sorted(textf),
        "injected_event_loop_failures": sorted(eventf),
        "injected_nondeterministic": sorted(nondet),
        "injected_profile_mismatches": sorted(profile_bad),
        "force_display_fallback": force_display_fallback,
        "max_failures": max_failures,
        "total_failures": total_failures,
        "gate_pass": gate_pass,
        "digest": digest,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--inject-launch-failure",
        action="append",
        default=[],
        help="force launch failure for a case id",
    )
    parser.add_argument(
        "--inject-render-failure",
        action="append",
        default=[],
        help="force render failure for a case id",
    )
    parser.add_argument(
        "--inject-input-failure",
        action="append",
        default=[],
        help="force input failure for a case id",
    )
    parser.add_argument(
        "--inject-text-failure",
        action="append",
        default=[],
        help="force text failure for a case id",
    )
    parser.add_argument(
        "--inject-event-loop-failure",
        action="append",
        default=[],
        help="force event-loop failure for a case id",
    )
    parser.add_argument(
        "--inject-nondeterministic",
        action="append",
        default=[],
        help="force non-deterministic result for a case id",
    )
    parser.add_argument(
        "--inject-profile-mismatch",
        action="append",
        default=[],
        help="force profile mismatch for a case id",
    )
    parser.add_argument("--max-failures", type=int, default=0)
    parser.add_argument(
        "--force-display-fallback",
        action="store_true",
        help="select the efifb display runtime path while keeping toolkit checks active",
    )
    parser.add_argument("--out", default="out/toolkit-compat-v1.json")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.max_failures < 0:
        print("error: max-failures must be >= 0")
        return 2

    injections = {
        "inject-launch-failure": _normalize_case_ids(args.inject_launch_failure),
        "inject-render-failure": _normalize_case_ids(args.inject_render_failure),
        "inject-input-failure": _normalize_case_ids(args.inject_input_failure),
        "inject-text-failure": _normalize_case_ids(args.inject_text_failure),
        "inject-event-loop-failure": _normalize_case_ids(args.inject_event_loop_failure),
        "inject-nondeterministic": _normalize_case_ids(args.inject_nondeterministic),
        "inject-profile-mismatch": _normalize_case_ids(args.inject_profile_mismatch),
    }
    try:
        for label, ids in injections.items():
            _validate_case_ids(label, ids)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    report = run_toolkit_compat(
        seed=args.seed,
        launch_failures=injections["inject-launch-failure"],
        render_failures=injections["inject-render-failure"],
        input_failures=injections["inject-input-failure"],
        text_failures=injections["inject-text-failure"],
        event_loop_failures=injections["inject-event-loop-failure"],
        nondeterministic=injections["inject-nondeterministic"],
        profile_mismatches=injections["inject-profile-mismatch"],
        max_failures=args.max_failures,
        force_display_fallback=args.force_display_fallback,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"toolkit-compat-report: {out_path}")
    print(f"issues: {len(report['issues'])}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
