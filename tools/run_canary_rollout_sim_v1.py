#!/usr/bin/env python3
"""Simulate staged canary rollout and promotion checks."""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def run_sim(seed: int, max_error_rate: float) -> Dict[str, object]:
    rng = random.Random(seed)
    stages = []
    halted = False
    for name, fraction in [("canary", 0.01), ("small_batch", 0.1), ("broad", 1.0)]:
        error_rate = round(rng.uniform(0.001, 0.015), 4)
        promoted = error_rate <= max_error_rate and not halted
        if not promoted:
            halted = True
        stages.append(
            {
                "stage": name,
                "fraction": fraction,
                "error_rate": error_rate,
                "threshold": max_error_rate,
                "promoted": promoted,
            }
        )
    return {
        "schema": "rugo.canary_rollout_report.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed": seed,
        "halted": halted,
        "stages": stages,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed", type=int, default=20260305)
    p.add_argument("--max-error-rate", type=float, default=0.02)
    p.add_argument("--out", default="out/canary-rollout-sim-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    report = run_sim(seed=args.seed, max_error_rate=args.max_error_rate)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"canary-rollout-report: {out_path}")
    print(f"halted: {report['halted']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

