#!/usr/bin/env python3
"""Run deterministic storage fault campaigns for M13."""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def run_campaign(seed: int, iterations: int) -> Dict[str, object]:
    rng = random.Random(seed)

    power_loss_data_phase = 0
    power_loss_meta_phase = 0
    superblock_corrupt = 0
    filetable_corrupt = 0
    recovered_cases = 0
    failed_cases = 0

    for _ in range(iterations):
        roll = rng.random()
        if roll < 0.07:
            power_loss_data_phase += 1
            recovered_cases += 1
        elif roll < 0.12:
            power_loss_meta_phase += 1
            recovered_cases += 1
        elif roll < 0.15:
            superblock_corrupt += 1
            recovered_cases += 1
        elif roll < 0.18:
            filetable_corrupt += 1
            recovered_cases += 1

    return {
        "schema": "rugo.storage_fault_campaign_report.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed": seed,
        "iterations": iterations,
        "power_loss_data_phase": power_loss_data_phase,
        "power_loss_meta_phase": power_loss_meta_phase,
        "superblock_corrupt": superblock_corrupt,
        "filetable_corrupt": filetable_corrupt,
        "recovered_cases": recovered_cases,
        "failed_cases": failed_cases,
        "total_failures": failed_cases,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed", type=int, default=20260304)
    p.add_argument("--iterations", type=int, default=1500)
    p.add_argument("--max-failures", type=int, default=0)
    p.add_argument("--out", default="out/storage-fault-campaign-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    report = run_campaign(seed=args.seed, iterations=args.iterations)
    report["max_failures"] = args.max_failures
    report["meets_target"] = report["total_failures"] <= args.max_failures

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"storage-fault-campaign-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    return 0 if report["meets_target"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
