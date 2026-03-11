#!/usr/bin/env python3
"""Run deterministic GUI runtime + toolkit bridge checks for M51."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple

import run_window_system_runtime_v1 as window_runtime


SCHEMA = "rugo.gui_runtime_report.v1"
CONTRACT_ID = "rugo.gui_runtime_contract.v1"
TOOLKIT_PROFILE_ID = "rugo.toolkit_profile.v1"
FONT_POLICY_ID = "rugo.font_text_rendering_policy.v1"
WINDOW_MANAGER_CONTRACT_ID = "rugo.window_manager_contract.v2"
WINDOW_RUNTIME_SCHEMA = "rugo.window_system_runtime_report.v1"
DISPLAY_RUNTIME_SCHEMA = "rugo.display_runtime_report.v1"
INPUT_RUNTIME_SCHEMA = "rugo.input_seat_runtime_report.v1"
TOOLKIT_COMPAT_SCHEMA = "rugo.toolkit_compat_report.v1"
DEFAULT_SEED = 20260311
RETAIN_PROFILE = "rugo.widgets.retain.v1"
OVERLAY_PROFILE = "rugo.canvas.overlay.v1"


@dataclass(frozen=True)
class CheckSpec:
    check_id: str
    domain: str
    metric_key: str
    operator: str
    threshold: float
    base: float
    spread: int
    scale: float


@dataclass(frozen=True)
class AppSpec:
    app_id: str
    window_id: str
    surface_id: str
    toolkit_profile: str
    role: str
    input_required: bool


BASE_CHECKS: Sequence[CheckSpec] = (
    CheckSpec(
        check_id="app_launch_budget",
        domain="launch",
        metric_key="launch_latency_p95_ms",
        operator="max",
        threshold=90.0,
        base=42.0,
        spread=12,
        scale=2.5,
    ),
    CheckSpec(
        check_id="launch_surface_bind_integrity",
        domain="launch",
        metric_key="surface_bind_mismatch_count",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="first_frame_budget",
        domain="render",
        metric_key="first_frame_latency_p95_ms",
        operator="max",
        threshold=50.0,
        base=24.0,
        spread=10,
        scale=1.6,
    ),
    CheckSpec(
        check_id="frame_present_budget",
        domain="render",
        metric_key="frame_latency_p95_ms",
        operator="max",
        threshold=16.667,
        base=12.15,
        spread=8,
        scale=0.25,
    ),
    CheckSpec(
        check_id="input_roundtrip_budget",
        domain="render",
        metric_key="input_roundtrip_latency_p95_ms",
        operator="max",
        threshold=22.0,
        base=10.8,
        spread=10,
        scale=0.8,
    ),
    CheckSpec(
        check_id="text_glyph_cache_integrity",
        domain="text",
        metric_key="missing_glyph_count",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="font_fallback_integrity",
        domain="text",
        metric_key="font_fallback_violation_count",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="baseline_grid_alignment",
        domain="text",
        metric_key="baseline_grid_violation_count",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="event_loop_wakeup_budget",
        domain="event_loop",
        metric_key="event_loop_wakeup_latency_p95_ms",
        operator="max",
        threshold=8.0,
        base=3.7,
        spread=9,
        scale=0.3,
    ),
    CheckSpec(
        check_id="event_queue_drain_budget",
        domain="event_loop",
        metric_key="event_queue_drain_latency_p95_ms",
        operator="max",
        threshold=12.0,
        base=5.8,
        spread=9,
        scale=0.45,
    ),
    CheckSpec(
        check_id="callback_order_integrity",
        domain="event_loop",
        metric_key="callback_reorder_count",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
)

SOURCE_CHECK_IDS = {
    "window_system_live",
    "toolkit_profiles_declared",
    "font_policy_declared",
}

APP_SPECS: Sequence[AppSpec] = (
    AppSpec(
        app_id="desktop.shell.workspace",
        window_id="desktop.shell.workspace",
        surface_id="surface.desktop.workspace",
        toolkit_profile=RETAIN_PROFILE,
        role="workspace-shell",
        input_required=False,
    ),
    AppSpec(
        app_id="files.panel",
        window_id="files.panel",
        surface_id="surface.files.panel",
        toolkit_profile=RETAIN_PROFILE,
        role="file-browser",
        input_required=True,
    ),
    AppSpec(
        app_id="settings.panel",
        window_id="settings.panel",
        surface_id="surface.settings.panel",
        toolkit_profile=RETAIN_PROFILE,
        role="settings-editor",
        input_required=True,
    ),
    AppSpec(
        app_id="toast.network",
        window_id="toast.network",
        surface_id="surface.toast.network",
        toolkit_profile=OVERLAY_PROFILE,
        role="overlay-toast",
        input_required=False,
    ),
)


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


def _metric(seed: int, key: str, label: str, base: float, spread: int, scale: float) -> float:
    return _round_value(base + ((_noise(seed, f"{key}|{label}") % spread) * scale))


def _count(seed: int, key: str, label: str, base: int, spread: int) -> int:
    return base + (_noise(seed, f"{key}|{label}") % spread)


def _window_entry(report: Dict[str, object], window_id: str) -> Tuple[Dict[str, object], bool]:
    for entry in report["surfaces"]:
        if entry["window_id"] == window_id:
            return entry, False
    for entry in report["retired_surfaces"]:
        if entry["window_id"] == window_id:
            return entry, True
    raise ValueError(f"missing window entry for {window_id!r}")


def normalize_failures(values: Sequence[str]) -> Set[str]:
    failures = {value.strip() for value in values if value.strip()}
    unknown = sorted(failures - known_checks())
    if unknown:
        raise ValueError(f"unknown check ids in --inject-failure: {', '.join(unknown)}")
    return failures


def run_gui_runtime(
    seed: int,
    injected_failures: Set[str] | None = None,
    max_failures: int = 0,
    force_display_fallback: bool = False,
) -> Dict[str, object]:
    failures = set() if injected_failures is None else set(injected_failures)

    window_report = window_runtime.run_window_system_runtime(
        seed=seed,
        max_failures=0,
        force_display_fallback=force_display_fallback,
    )

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

    surface_mismatches = sum(
        1
        for spec in APP_SPECS
        if _window_entry(window_report, spec.window_id)[0]["surface_id"] != spec.surface_id
    )
    if "launch_surface_bind_integrity" not in failures:
        metric_values["surface_bind_mismatch_count"] = float(surface_mismatches)
        checks[1]["observed"] = float(surface_mismatches)
        checks[1]["pass"] = surface_mismatches == 0

    source_rows = [
        {
            "check_id": "window_system_live",
            "domain": "source",
            "metric_key": "window_system_ready_ratio",
            "operator": "min",
            "threshold": 1.0,
            "observed": 0.0,
        },
        {
            "check_id": "toolkit_profiles_declared",
            "domain": "source",
            "metric_key": "toolkit_profile_count",
            "operator": "eq",
            "threshold": 2.0,
            "observed": 2.0,
        },
        {
            "check_id": "font_policy_declared",
            "domain": "source",
            "metric_key": "font_policy_ready_ratio",
            "operator": "min",
            "threshold": 1.0,
            "observed": 1.0,
        },
    ]
    source_rows[0]["observed"] = (
        0.0
        if "window_system_live" in failures
        else 1.0 if window_report["gate_pass"] else 0.0
    )
    source_rows[1]["observed"] = (
        _failing_observed("eq", 2.0, 0.0)
        if "toolkit_profiles_declared" in failures
        else 2.0
    )
    source_rows[2]["observed"] = 0.0 if "font_policy_declared" in failures else 1.0

    for row in source_rows:
        passed = _passes(row["operator"], float(row["observed"]), float(row["threshold"]))
        checks.append({**row, "pass": passed})
        metric_values[row["metric_key"]] = float(row["observed"])

    check_pass = {row["check_id"]: bool(row["pass"]) for row in checks}

    text_checks_pass = all(
        check_pass[name]
        for name in (
            "text_glyph_cache_integrity",
            "font_fallback_integrity",
            "baseline_grid_alignment",
        )
    )
    event_loop_checks_pass = all(
        check_pass[name]
        for name in (
            "event_loop_wakeup_budget",
            "event_queue_drain_budget",
            "callback_order_integrity",
        )
    )

    apps: List[Dict[str, object]] = []
    for spec in APP_SPECS:
        entry, retired = _window_entry(window_report, spec.window_id)
        launch_ready = check_pass["app_launch_budget"] and check_pass["launch_surface_bind_integrity"]
        render_ready = check_pass["first_frame_budget"] and check_pass["frame_present_budget"]
        input_ready = (not spec.input_required) or check_pass["input_roundtrip_budget"]
        checks_pass = (
            launch_ready
            and render_ready
            and input_ready
            and text_checks_pass
            and event_loop_checks_pass
            and check_pass["window_system_live"]
        )
        apps.append(
            {
                "app_id": spec.app_id,
                "window_id": spec.window_id,
                "surface_id": spec.surface_id,
                "toolkit_profile": spec.toolkit_profile,
                "role": spec.role,
                "retired": retired,
                "state": entry["final_state"] if retired else entry["state"],
                "focused": False if retired else entry["focused"],
                "launch_ms": _metric(seed, spec.app_id, "launch", base=28.0, spread=11, scale=2.2),
                "first_frame_ms": _metric(
                    seed, spec.app_id, "first_frame", base=15.0, spread=10, scale=1.6
                ),
                "frame_latency_p95_ms": _metric(
                    seed, spec.app_id, "frame", base=10.6, spread=8, scale=0.4
                ),
                "input_latency_p95_ms": (
                    _metric(seed, spec.app_id, "input", base=8.4, spread=10, scale=0.7)
                    if spec.input_required
                    else 0.0
                ),
                "input_required": spec.input_required,
                "launch_ok": launch_ready,
                "render_ok": render_ready,
                "input_ok": input_ready,
                "text_ok": text_checks_pass,
                "event_loop_ok": event_loop_checks_pass,
                "checks_pass": checks_pass,
            }
        )

    retain_apps = [app["app_id"] for app in apps if app["toolkit_profile"] == RETAIN_PROFILE]
    overlay_apps = [app["app_id"] for app in apps if app["toolkit_profile"] == OVERLAY_PROFILE]

    toolkit_profiles = {
        RETAIN_PROFILE: {
            "profile_id": RETAIN_PROFILE,
            "render_model": "retained-scene",
            "text_backend": "atlas-text",
            "input_modes": ["keyboard", "pointer", "focus"],
            "supported_primitives": [
                "label",
                "button",
                "text_field",
                "scroll_view",
                "panel",
            ],
            "apps": retain_apps,
            "checks_pass": all(
                app["checks_pass"] for app in apps if app["toolkit_profile"] == RETAIN_PROFILE
            ),
        },
        OVERLAY_PROFILE: {
            "profile_id": OVERLAY_PROFILE,
            "render_model": "immediate-overlay",
            "text_backend": "atlas-text",
            "input_modes": ["timer", "pointer-pass-through"],
            "supported_primitives": ["toast", "icon", "label", "panel"],
            "apps": overlay_apps,
            "checks_pass": all(
                app["checks_pass"] for app in apps if app["toolkit_profile"] == OVERLAY_PROFILE
            ),
        },
    }

    font_text = {
        "policy_id": FONT_POLICY_ID,
        "default_font_family": "rugo-sans",
        "fallback_font_family": "rugo-mono",
        "shaping_profile": "ascii-plus-latin-1-no-complex-shaping",
        "raster_mode": "grayscale-atlas",
        "subpixel_mode": "disabled",
        "baseline_grid_px": 4,
        "glyph_cache_entries": _count(seed, "font-text", "glyphs", base=164, spread=16),
        "atlas_pages": 1,
        "missing_glyph_count": int(metric_values["missing_glyph_count"]),
        "fallback_events": 1,
        "font_fallback_violation_count": int(metric_values["font_fallback_violation_count"]),
        "baseline_grid_violation_count": int(metric_values["baseline_grid_violation_count"]),
        "text_samples": [
            {
                "app_id": "desktop.shell.workspace",
                "sample_id": "workspace-title",
                "font_family": "rugo-sans",
                "glyph_count": 24,
            },
            {
                "app_id": "files.panel",
                "sample_id": "path-listing",
                "font_family": "rugo-mono",
                "glyph_count": 46,
            },
            {
                "app_id": "settings.panel",
                "sample_id": "settings-sections",
                "font_family": "rugo-sans",
                "glyph_count": 38,
            },
            {
                "app_id": "toast.network",
                "sample_id": "toast-label",
                "font_family": "rugo-sans",
                "glyph_count": 18,
            },
        ],
        "checks_pass": text_checks_pass,
    }

    event_loop = {
        "dispatch_model": "single-ui-thread-plus-runtime-queue",
        "callback_order": ["input", "layout", "paint", "present"],
        "callback_reorder_count": int(metric_values["callback_reorder_count"]),
        "frame_clock_hz": 60,
        "wakeup_latency_p95_ms": metric_values["event_loop_wakeup_latency_p95_ms"],
        "queue_drain_latency_p95_ms": metric_values["event_queue_drain_latency_p95_ms"],
        "queue_depth_p95": _count(seed, "event-loop", "queue-depth", base=2, spread=3),
        "timers": [
            {"name": "cursor-blink", "period_ms": 500},
            {"name": "toast-expire", "period_ms": 3000},
        ],
        "active_focus_app": window_report["seat"]["focus_owner"],
        "checks_pass": event_loop_checks_pass,
    }

    stable_payload = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "toolkit_profile_id": TOOLKIT_PROFILE_ID,
        "font_policy_id": FONT_POLICY_ID,
        "seed": seed,
        "checks": [
            {
                "check_id": row["check_id"],
                "domain": row["domain"],
                "pass": row["pass"],
                "observed": row["observed"],
            }
            for row in checks
        ],
        "apps": [
            {
                "app_id": app["app_id"],
                "toolkit_profile": app["toolkit_profile"],
                "state": app["state"],
                "checks_pass": app["checks_pass"],
            }
            for app in apps
        ],
        "window_digest": window_report["digest"],
        "font_text": {
            "glyph_cache_entries": font_text["glyph_cache_entries"],
            "missing_glyph_count": font_text["missing_glyph_count"],
            "font_fallback_violation_count": font_text["font_fallback_violation_count"],
        },
        "event_loop": {
            "wakeup_latency_p95_ms": event_loop["wakeup_latency_p95_ms"],
            "queue_drain_latency_p95_ms": event_loop["queue_drain_latency_p95_ms"],
            "callback_reorder_count": event_loop["callback_reorder_count"],
        },
    }
    digest = hashlib.sha256(
        json.dumps(stable_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    failures_list = sorted(row["check_id"] for row in checks if row["pass"] is False)
    total_failures = len(failures_list)
    gate_pass = total_failures <= max_failures

    summary = {
        "launch": _domain_summary(checks, "launch"),
        "render": _domain_summary(checks, "render"),
        "text": _domain_summary(checks, "text"),
        "event_loop": _domain_summary(checks, "event_loop"),
        "source": _domain_summary(checks, "source"),
    }

    return {
        "schema": SCHEMA,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "contract_id": CONTRACT_ID,
        "toolkit_profile_id": TOOLKIT_PROFILE_ID,
        "font_policy_id": FONT_POLICY_ID,
        "window_manager_contract_id": WINDOW_MANAGER_CONTRACT_ID,
        "window_runtime_schema": WINDOW_RUNTIME_SCHEMA,
        "display_runtime_schema": DISPLAY_RUNTIME_SCHEMA,
        "input_runtime_schema": INPUT_RUNTIME_SCHEMA,
        "toolkit_compat_schema": TOOLKIT_COMPAT_SCHEMA,
        "seed": seed,
        "gate": "test-gui-runtime-v1",
        "toolkit_gate": "test-toolkit-compat-v1",
        "checks": checks,
        "summary": summary,
        "runtime_topology": {
            "output_id": window_report["output"]["output_id"],
            "width": window_report["output"]["width"],
            "height": window_report["output"]["height"],
            "active_display_path": window_report["output"]["active_display_path"],
            "active_display_driver": window_report["output"]["active_display_driver"],
            "seat_id": window_report["seat"]["seat_id"],
            "focus_owner": window_report["seat"]["focus_owner"],
            "focus_owner_surface_id": window_report["seat"]["focus_owner_surface_id"],
            "active_app_count": len([app for app in apps if not app["retired"]]),
            "retired_app_count": len([app for app in apps if app["retired"]]),
            "toolkit_profile_count": int(metric_values["toolkit_profile_count"]),
        },
        "apps": apps,
        "toolkit_profiles": toolkit_profiles,
        "font_text": font_text,
        "event_loop": event_loop,
        "source_reports": {
            "window_system": {
                "schema": window_report["schema"],
                "digest": window_report["digest"],
                "gate_pass": window_report["gate_pass"],
                "focus_owner": window_report["seat"]["focus_owner"],
                "output_id": window_report["output"]["output_id"],
            },
            "display_runtime": {
                "schema": window_report["source_reports"]["display_runtime"]["schema"],
                "digest": window_report["source_reports"]["display_runtime"]["digest"],
                "gate_pass": window_report["source_reports"]["display_runtime"]["gate_pass"],
                "active_runtime_path": window_report["source_reports"]["display_runtime"][
                    "active_runtime_path"
                ],
                "active_runtime_driver": window_report["source_reports"]["display_runtime"][
                    "active_runtime_driver"
                ],
            },
            "input_seat": {
                "schema": window_report["source_reports"]["input_seat"]["schema"],
                "digest": window_report["source_reports"]["input_seat"]["digest"],
                "gate_pass": window_report["source_reports"]["input_seat"]["gate_pass"],
                "seat_id": window_report["source_reports"]["input_seat"]["seat_id"],
                "focus_owner": window_report["source_reports"]["input_seat"]["focus_owner"],
            },
        },
        "artifact_refs": {
            "junit": "out/pytest-gui-runtime-v1.xml",
            "runtime_report": "out/gui-runtime-v1.json",
            "toolkit_compat_report": "out/toolkit-compat-v1.json",
            "window_system_report": "out/window-system-v1.json",
            "display_runtime_report": "out/display-runtime-v1.json",
            "input_seat_report": "out/input-seat-v1.json",
            "ci_artifact": "gui-runtime-v1-artifacts",
            "toolkit_ci_artifact": "toolkit-compat-v1-artifacts",
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
        help="force a GUI runtime check to fail by check_id",
    )
    parser.add_argument("--max-failures", type=int, default=0)
    parser.add_argument(
        "--force-display-fallback",
        action="store_true",
        help="select the efifb display runtime path while keeping GUI checks active",
    )
    parser.add_argument("--out", default="out/gui-runtime-v1.json")
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

    report = run_gui_runtime(
        seed=args.seed,
        injected_failures=injected_failures,
        max_failures=args.max_failures,
        force_display_fallback=args.force_display_fallback,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"gui-runtime-report: {out_path}")
    print(f"focus_app: {report['runtime_topology']['focus_owner']}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
