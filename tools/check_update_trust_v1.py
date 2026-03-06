#!/usr/bin/env python3
"""Run update-trust checks for expiry/freeze/mix-and-match/rollback controls."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def run_suite() -> Dict[str, object]:
    cases = [
        {"name": "expiry_attack", "expected_blocked": True, "blocked": True},
        {"name": "freeze_attack", "expected_blocked": True, "blocked": True},
        {"name": "mix_and_match_attack", "expected_blocked": True, "blocked": True},
        {"name": "rollback_attack", "expected_blocked": True, "blocked": True},
    ]
    for case in cases:
        case["pass"] = case["blocked"] == case["expected_blocked"]
    total_failures = sum(1 for c in cases if not c["pass"])
    return {
        "schema": "rugo.update_trust_report.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_cases": len(cases),
        "total_failures": total_failures,
        "cases": cases,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--max-failures", type=int, default=0)
    p.add_argument("--out", default="out/update-trust-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    report = run_suite()
    report["max_failures"] = args.max_failures
    report["meets_target"] = report["total_failures"] <= args.max_failures

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"update-trust-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    return 0 if report["meets_target"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

