#!/usr/bin/env python3
"""Run deterministic security embargo workflow drill."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


POLICY_ID = "rugo.vulnerability_response_policy.v1"
STEP_SPECS = [
    ("private_intake", 2),
    ("triage_complete", 10),
    ("fix_prepared", 30),
    ("coordinated_publish", 36),
]


def _known_step_names() -> set[str]:
    return {name for name, _ in STEP_SPECS}


def _collect_injected_failures(values: List[str]) -> set[str]:
    requested = {value.strip() for value in values if value.strip()}
    unknown = sorted(requested - _known_step_names())
    if unknown:
        raise ValueError(f"unknown drill steps in --inject-failure: {', '.join(unknown)}")
    return requested


def run_drill(
    triage_sla_hours: int = 24,
    injected_failures: set[str] | None = None,
) -> Dict[str, object]:
    forced_failures = set() if injected_failures is None else set(injected_failures)
    steps = [
        {
            "name": name,
            "elapsed_hours": elapsed,
            "success": name not in forced_failures,
        }
        for name, elapsed in STEP_SPECS
    ]

    triage_elapsed = next(
        int(step["elapsed_hours"]) for step in steps if step["name"] == "triage_complete"
    )
    workflow_success = all(bool(step["success"]) for step in steps)
    meets_sla = triage_elapsed <= triage_sla_hours and workflow_success
    total_failures = sum(1 for step in steps if not step["success"])
    if triage_elapsed > triage_sla_hours:
        total_failures += 1

    return {
        "schema": "rugo.security_embargo_drill_report.v1",
        "policy_id": POLICY_ID,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "triage_sla_hours": triage_sla_hours,
        "triage_elapsed_hours": triage_elapsed,
        "meets_sla": meets_sla,
        "total_failures": total_failures,
        "steps": steps,
        "success": meets_sla and total_failures == 0,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--triage-sla-hours", type=int, default=24)
    p.add_argument(
        "--inject-failure",
        action="append",
        default=[],
        help="force a named embargo workflow step to fail",
    )
    p.add_argument("--out", default="out/security-embargo-drill-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        injected = _collect_injected_failures(args.inject_failure)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    report = run_drill(
        triage_sla_hours=args.triage_sla_hours,
        injected_failures=injected,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"security-embargo-drill: {out_path}")
    print(f"meets_sla: {report['meets_sla']}")
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
