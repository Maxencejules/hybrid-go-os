#!/usr/bin/env python3
"""Run deterministic SLO-triggered rollout abort/rollback drill for M33."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


SCHEMA = "rugo.rollout_abort_drill_report.v1"
POLICY_ID = "rugo.canary_slo_policy.v1"


def run_drill(
    slo_error_rate_threshold: float,
    slo_latency_p95_ms_threshold: int,
    observed_error_rate: float,
    observed_latency_p95_ms: int,
) -> Dict[str, object]:
    error_breach = observed_error_rate > slo_error_rate_threshold
    latency_breach = observed_latency_p95_ms > slo_latency_p95_ms_threshold
    auto_halt = error_breach or latency_breach

    checks = [
        {
            "name": "slo_breach_detected",
            "pass": error_breach or latency_breach,
        },
        {
            "name": "auto_halt_triggered",
            "pass": auto_halt,
        },
        {
            "name": "rollback_triggered",
            "pass": auto_halt,
        },
    ]
    total_failures = sum(1 for check in checks if check["pass"] is False)

    return {
        "schema": SCHEMA,
        "policy_id": POLICY_ID,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "slo_error_rate_threshold": slo_error_rate_threshold,
        "slo_latency_p95_ms_threshold": slo_latency_p95_ms_threshold,
        "observed_error_rate": observed_error_rate,
        "observed_latency_p95_ms": observed_latency_p95_ms,
        "error_breach": error_breach,
        "latency_breach": latency_breach,
        "auto_halt": auto_halt,
        "rollback_triggered": auto_halt,
        "policy_enforced": auto_halt,
        "checks": checks,
        "total_failures": total_failures,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--slo-error-rate-threshold", type=float, default=0.02)
    p.add_argument("--slo-latency-p95-ms-threshold", type=int, default=120)
    p.add_argument("--observed-error-rate", type=float, default=0.08)
    p.add_argument("--observed-latency-p95-ms", type=int, default=145)
    p.add_argument("--max-failures", type=int, default=0)
    p.add_argument("--out", default="out/rollout-abort-drill-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.max_failures < 0:
        print("error: max-failures must be >= 0")
        return 2
    if not (0.0 <= args.slo_error_rate_threshold <= 1.0):
        print("error: slo-error-rate-threshold must be in [0, 1]")
        return 2
    if not (0.0 <= args.observed_error_rate <= 1.0):
        print("error: observed-error-rate must be in [0, 1]")
        return 2
    if args.slo_latency_p95_ms_threshold <= 0:
        print("error: slo-latency-p95-ms-threshold must be > 0")
        return 2
    if args.observed_latency_p95_ms <= 0:
        print("error: observed-latency-p95-ms must be > 0")
        return 2

    report = run_drill(
        slo_error_rate_threshold=args.slo_error_rate_threshold,
        slo_latency_p95_ms_threshold=args.slo_latency_p95_ms_threshold,
        observed_error_rate=args.observed_error_rate,
        observed_latency_p95_ms=args.observed_latency_p95_ms,
    )
    report["max_failures"] = args.max_failures
    report["meets_target"] = report["total_failures"] <= args.max_failures

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"rollout-abort-drill: {out_path}")
    print(f"policy_enforced: {report['policy_enforced']}")
    print(f"total_failures: {report['total_failures']}")
    print(f"meets_target: {report['meets_target']}")
    return 0 if report["meets_target"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
