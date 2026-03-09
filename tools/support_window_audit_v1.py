#!/usr/bin/env python3
"""Audit support-window and backport obligations for M31 lifecycle gate."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


SCHEMA = "rugo.support_window_audit.v1"
POLICY_ID = "rugo.support_lifecycle_policy.v1"
DEFAULT_WINDOWS = [
    "stable:180:45:7:90",
    "lts:730:140:14:365",
    "beta:45:12:5:21",
]


def _parse_window_spec(spec: str) -> Dict[str, object]:
    parts = spec.split(":")
    if len(parts) != 5:
        raise ValueError(
            "window spec must be '<channel>:<support_days>:<age_days>:"
            "<security_sla_days>:<backport_window_days>'"
        )
    channel, support_days, age_days, security_sla_days, backport_window_days = parts
    try:
        support_days_value = int(support_days)
        age_days_value = int(age_days)
        security_sla_days_value = int(security_sla_days)
        backport_window_days_value = int(backport_window_days)
    except ValueError as exc:
        raise ValueError("window spec numeric fields must be integers") from exc
    if support_days_value <= 0:
        raise ValueError("support_days must be > 0")
    if age_days_value < 0:
        raise ValueError("age_days must be >= 0")
    if security_sla_days_value <= 0:
        raise ValueError("security_sla_days must be > 0")
    if backport_window_days_value <= 0:
        raise ValueError("backport_window_days must be > 0")
    return {
        "channel": channel,
        "support_days": support_days_value,
        "age_days": age_days_value,
        "security_sla_days": security_sla_days_value,
        "backport_window_days": backport_window_days_value,
    }


def run_audit(
    window_specs: List[str],
    required_channels: List[str],
    max_security_sla_days: int,
    min_backport_window_days: int,
) -> Dict[str, object]:
    required = list(dict.fromkeys(required_channels))
    windows: List[Dict[str, object]] = []
    for spec in window_specs:
        entry = _parse_window_spec(spec)
        entry["in_support"] = entry["age_days"] <= entry["support_days"]
        entry["security_sla_within_threshold"] = (
            entry["security_sla_days"] <= max_security_sla_days
        )
        entry["backport_window_meets_floor"] = (
            entry["backport_window_days"] >= min_backport_window_days
        )
        windows.append(entry)

    channels = [str(entry["channel"]) for entry in windows]
    unique_channels = list(dict.fromkeys(channels))
    missing_required = [channel for channel in required if channel not in unique_channels]
    duplicate_channels = sorted(
        {channel for channel in channels if channels.count(channel) > 1}
    )

    checks = [
        {
            "name": "window_set_non_empty",
            "pass": len(windows) > 0,
        },
        {
            "name": "required_channels_present",
            "pass": len(missing_required) == 0,
        },
        {
            "name": "channels_unique",
            "pass": len(duplicate_channels) == 0,
        },
        {
            "name": "all_channels_within_support_window",
            "pass": all(entry["in_support"] for entry in windows),
        },
        {
            "name": "security_sla_within_threshold",
            "pass": all(entry["security_sla_within_threshold"] for entry in windows),
        },
        {
            "name": "backport_window_meets_floor",
            "pass": all(entry["backport_window_meets_floor"] for entry in windows),
        },
    ]
    total_failures = sum(1 for check in checks if check["pass"] is False)

    return {
        "schema": SCHEMA,
        "policy_id": POLICY_ID,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "required_channels": required,
        "max_security_sla_days": max_security_sla_days,
        "min_backport_window_days": min_backport_window_days,
        "windows": windows,
        "missing_required_channels": missing_required,
        "duplicate_channels": duplicate_channels,
        "checks": checks,
        "total_failures": total_failures,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window", action="append", default=[])
    parser.add_argument("--required-channel", action="append", default=["stable", "lts"])
    parser.add_argument("--max-security-sla-days", type=int, default=14)
    parser.add_argument("--min-backport-window-days", type=int, default=21)
    parser.add_argument("--max-failures", type=int, default=0)
    parser.add_argument("--out", default="out/support-window-audit-v1.json")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.max_security_sla_days <= 0:
        print("error: max-security-sla-days must be > 0")
        return 2
    if args.min_backport_window_days <= 0:
        print("error: min-backport-window-days must be > 0")
        return 2

    window_specs = args.window or list(DEFAULT_WINDOWS)
    try:
        report = run_audit(
            window_specs=window_specs,
            required_channels=args.required_channel,
            max_security_sla_days=args.max_security_sla_days,
            min_backport_window_days=args.min_backport_window_days,
        )
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    report["max_failures"] = args.max_failures
    report["meets_target"] = report["total_failures"] <= args.max_failures

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"support-window-audit: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    return 0 if report["meets_target"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
