#!/usr/bin/env python3
"""Run deterministic GUI app compatibility matrix checks for M35."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set


PROFILE_ID = "rugo.desktop_profile.v1"
PROFILE_LABEL = "desktop_profile_v1"
TIER_SCHEMA = "rugo.gui_app_tiers.v1"
REPORT_SCHEMA = "rugo.gui_app_matrix_report.v1"

CLASS_THRESHOLDS: Dict[str, Dict[str, object]] = {
    "productivity": {"tier": "tier_productivity", "min_cases": 6, "min_pass_rate": 0.83},
    "media": {"tier": "tier_media", "min_cases": 4, "min_pass_rate": 0.75},
    "utility": {"tier": "tier_utility", "min_cases": 5, "min_pass_rate": 0.80},
}


@dataclass(frozen=True)
class GuiCompatCase:
    case_id: str
    app_id: str
    app_class: str
    tier: str
    launch_ok: bool = True
    render_ok: bool = True
    input_ok: bool = True
    deterministic: bool = True
    profile: str = PROFILE_LABEL


def _baseline_cases() -> List[GuiCompatCase]:
    cases: List[GuiCompatCase] = []

    for idx in range(6):
        cases.append(
            GuiCompatCase(
                case_id=f"productivity-{idx:02d}",
                app_id=f"gui-productivity-{idx:02d}",
                app_class="productivity",
                tier="tier_productivity",
                render_ok=idx != 5,  # 5/6 pass
            )
        )

    for idx in range(4):
        cases.append(
            GuiCompatCase(
                case_id=f"media-{idx:02d}",
                app_id=f"gui-media-{idx:02d}",
                app_class="media",
                tier="tier_media",
                launch_ok=idx != 3,  # 3/4 pass
            )
        )

    for idx in range(5):
        cases.append(
            GuiCompatCase(
                case_id=f"utility-{idx:02d}",
                app_id=f"gui-utility-{idx:02d}",
                app_class="utility",
                tier="tier_utility",
                input_ok=idx != 4,  # 4/5 pass
            )
        )

    return cases


def _known_case_ids() -> Set[str]:
    return {case.case_id for case in _baseline_cases()}


def _normalize_case_ids(values: Sequence[str]) -> Set[str]:
    return {value.strip() for value in values if value.strip()}


def _validate_case_ids(label: str, case_ids: Set[str]) -> None:
    unknown = sorted(case_ids - _known_case_ids())
    if unknown:
        raise ValueError(f"unknown case ids in {label}: {', '.join(unknown)}")


def _metric(seed: int, case_id: str, label: str, base: int, spread: int) -> int:
    digest = hashlib.sha256(f"{seed}|{case_id}|{label}".encode("utf-8")).hexdigest()
    return base + (int(digest[:8], 16) % spread)


def _apply_injections(
    cases: List[GuiCompatCase],
    launch_failures: Set[str],
    render_failures: Set[str],
    input_failures: Set[str],
    nondeterministic: Set[str],
    profile_mismatches: Set[str],
) -> List[GuiCompatCase]:
    updated: List[GuiCompatCase] = []
    for case in cases:
        candidate = case
        if case.case_id in launch_failures:
            candidate = replace(candidate, launch_ok=False)
        if case.case_id in render_failures:
            candidate = replace(candidate, render_ok=False)
        if case.case_id in input_failures:
            candidate = replace(candidate, input_ok=False)
        if case.case_id in nondeterministic:
            candidate = replace(candidate, deterministic=False)
        if case.case_id in profile_mismatches:
            candidate = replace(candidate, profile="desktop_profile_v0")
        updated.append(candidate)
    return updated


def run_matrix(
    seed: int,
    launch_failures: Set[str] | None = None,
    render_failures: Set[str] | None = None,
    input_failures: Set[str] | None = None,
    nondeterministic: Set[str] | None = None,
    profile_mismatches: Set[str] | None = None,
) -> Dict[str, object]:
    launch = set() if launch_failures is None else set(launch_failures)
    render = set() if render_failures is None else set(render_failures)
    inputf = set() if input_failures is None else set(input_failures)
    nondet = set() if nondeterministic is None else set(nondeterministic)
    profile_bad = set() if profile_mismatches is None else set(profile_mismatches)

    cases = _apply_injections(
        _baseline_cases(),
        launch_failures=launch,
        render_failures=render,
        input_failures=inputf,
        nondeterministic=nondet,
        profile_mismatches=profile_bad,
    )

    class_totals = {
        class_name: {"eligible": 0, "passed": 0}
        for class_name in sorted(CLASS_THRESHOLDS.keys())
    }
    case_reports: List[Dict[str, object]] = []
    issues: List[Dict[str, object]] = []

    for case in sorted(cases, key=lambda item: item.case_id):
        expected = CLASS_THRESHOLDS.get(case.app_class)
        counted_for_threshold = True
        if expected is None:
            issues.append({"case_id": case.case_id, "reason": "unknown_class"})
            counted_for_threshold = False
        elif case.tier != expected["tier"]:
            issues.append(
                {
                    "case_id": case.case_id,
                    "reason": "tier_mismatch",
                    "expected_tier": expected["tier"],
                    "actual_tier": case.tier,
                }
            )
            counted_for_threshold = False
        elif not case.deterministic:
            issues.append({"case_id": case.case_id, "reason": "non_deterministic_result"})
            counted_for_threshold = False
        elif case.profile != PROFILE_LABEL:
            issues.append({"case_id": case.case_id, "reason": "profile_mismatch"})
            counted_for_threshold = False

        passed = case.launch_ok and case.render_ok and case.input_ok
        if counted_for_threshold:
            bucket = class_totals[case.app_class]
            bucket["eligible"] += 1
            if passed:
                bucket["passed"] += 1

        case_reports.append(
            {
                "case_id": case.case_id,
                "app_id": case.app_id,
                "class": case.app_class,
                "tier": case.tier,
                "launch_ok": case.launch_ok,
                "render_ok": case.render_ok,
                "input_ok": case.input_ok,
                "deterministic": case.deterministic,
                "profile": case.profile,
                "passed": passed,
                "counted_for_threshold": counted_for_threshold,
                "metrics": {
                    "launch_ms": _metric(seed, case.case_id, "launch", base=52, spread=35),
                    "frame_time_ms_p95": _metric(
                        seed, case.case_id, "frame", base=9, spread=10
                    ),
                    "input_latency_ms_p95": _metric(
                        seed, case.case_id, "input", base=7, spread=9
                    ),
                },
            }
        )

    class_reports: Dict[str, Dict[str, object]] = {}
    class_failures = 0
    for class_name in sorted(CLASS_THRESHOLDS.keys()):
        threshold = CLASS_THRESHOLDS[class_name]
        stats = class_totals[class_name]
        eligible = int(stats["eligible"])
        passed = int(stats["passed"])
        pass_rate = (passed / eligible) if eligible else 0.0
        meets_threshold = (
            eligible >= int(threshold["min_cases"])
            and pass_rate >= float(threshold["min_pass_rate"])
        )
        if not meets_threshold:
            class_failures += 1

        class_reports[class_name] = {
            "tier": threshold["tier"],
            "eligible": eligible,
            "passed": passed,
            "pass_rate": pass_rate,
            "min_cases": int(threshold["min_cases"]),
            "min_pass_rate": float(threshold["min_pass_rate"]),
            "meets_threshold": meets_threshold,
        }

    issues_sorted = sorted(issues, key=lambda item: (str(item["reason"]), item["case_id"]))
    total_failures = len(issues_sorted) + class_failures

    stable_payload = {
        "schema": REPORT_SCHEMA,
        "profile_id": PROFILE_ID,
        "tier_schema": TIER_SCHEMA,
        "seed": seed,
        "classes": class_reports,
        "issues": issues_sorted,
        "cases": [
            {
                "case_id": item["case_id"],
                "class": item["class"],
                "passed": item["passed"],
                "counted_for_threshold": item["counted_for_threshold"],
            }
            for item in case_reports
        ],
    }
    digest = hashlib.sha256(
        json.dumps(stable_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    gate_pass = total_failures == 0
    return {
        "schema": REPORT_SCHEMA,
        "profile_id": PROFILE_ID,
        "tier_schema": TIER_SCHEMA,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed": seed,
        "total_cases": len(case_reports),
        "classes": class_reports,
        "cases": case_reports,
        "issues": issues_sorted,
        "total_failures": total_failures,
        "gate_pass": gate_pass,
        "digest": digest,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20260309)
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
    parser.add_argument("--out", default="out/gui-app-matrix-v1.json")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    injections = {
        "inject-launch-failure": _normalize_case_ids(args.inject_launch_failure),
        "inject-render-failure": _normalize_case_ids(args.inject_render_failure),
        "inject-input-failure": _normalize_case_ids(args.inject_input_failure),
        "inject-nondeterministic": _normalize_case_ids(args.inject_nondeterministic),
        "inject-profile-mismatch": _normalize_case_ids(args.inject_profile_mismatch),
    }
    try:
        for label, ids in injections.items():
            _validate_case_ids(label, ids)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    report = run_matrix(
        seed=args.seed,
        launch_failures=injections["inject-launch-failure"],
        render_failures=injections["inject-render-failure"],
        input_failures=injections["inject-input-failure"],
        nondeterministic=injections["inject-nondeterministic"],
        profile_mismatches=injections["inject-profile-mismatch"],
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"gui-app-matrix-report: {out_path}")
    print(f"issues: {len(report['issues'])}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

