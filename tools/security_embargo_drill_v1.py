#!/usr/bin/env python3
"""Run deterministic security embargo workflow drill."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def run_drill() -> Dict[str, object]:
    steps = [
        {"name": "private_intake", "elapsed_hours": 2, "success": True},
        {"name": "triage_complete", "elapsed_hours": 10, "success": True},
        {"name": "fix_prepared", "elapsed_hours": 30, "success": True},
        {"name": "coordinated_publish", "elapsed_hours": 36, "success": True},
    ]
    triage_sla_hours = 24
    triage_elapsed = next(s["elapsed_hours"] for s in steps if s["name"] == "triage_complete")
    return {
        "schema": "rugo.security_embargo_drill_report.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "triage_sla_hours": triage_sla_hours,
        "triage_elapsed_hours": triage_elapsed,
        "meets_sla": triage_elapsed <= triage_sla_hours,
        "steps": steps,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default="out/security-embargo-drill-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    report = run_drill()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"security-embargo-drill: {out_path}")
    print(f"meets_sla: {report['meets_sla']}")
    return 0 if report["meets_sla"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

