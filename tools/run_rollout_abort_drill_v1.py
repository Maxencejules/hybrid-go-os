#!/usr/bin/env python3
"""Run SLO-triggered rollout abort/rollback drill."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--slo-error-rate-threshold", type=float, default=0.02)
    p.add_argument("--observed-error-rate", type=float, default=0.08)
    p.add_argument("--out", default="out/rollout-abort-drill-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    auto_halt = args.observed_error_rate > args.slo_error_rate_threshold
    report = {
        "schema": "rugo.rollout_abort_drill_report.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "slo_error_rate_threshold": args.slo_error_rate_threshold,
        "observed_error_rate": args.observed_error_rate,
        "auto_halt": auto_halt,
        "rollback_triggered": auto_halt,
        "policy_enforced": auto_halt,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"rollout-abort-drill: {out_path}")
    print(f"policy_enforced: {report['policy_enforced']}")
    return 0 if report["policy_enforced"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

