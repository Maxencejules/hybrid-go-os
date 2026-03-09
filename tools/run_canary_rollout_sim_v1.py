#!/usr/bin/env python3
"""Run deterministic staged rollout simulation for M33 rollout safety checks."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple


SCHEMA = "rugo.canary_rollout_report.v1"
POLICY_ID = "rugo.staged_rollout_policy.v1"
SLO_POLICY_ID = "rugo.canary_slo_policy.v1"
DEFAULT_SEED = 20260309
STAGES: Sequence[Tuple[str, float, int]] = (
    ("canary", 0.01, 120),
    ("small_batch", 0.10, 130),
    ("broad", 1.00, 150),
)


def _known_stages() -> Set[str]:
    return {stage for stage, _, _ in STAGES}


def _parse_injected_failures(values: Sequence[str]) -> Set[str]:
    requested = {value.strip() for value in values if value.strip()}
    unknown = sorted(requested - _known_stages())
    if unknown:
        raise ValueError(f"unknown stage ids in --inject-failure-stage: {', '.join(unknown)}")
    return requested


def _noise(seed: int, stage: str, metric: str) -> int:
    digest = hashlib.sha256(f"{seed}|{stage}|{metric}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 6


def run_sim(
    seed: int,
    max_error_rate: float,
    max_latency_p95_ms: int,
    injected_failure_stages: Set[str] | None = None,
) -> Dict[str, object]:
    failures = set() if injected_failure_stages is None else set(injected_failure_stages)
    stages: List[Dict[str, object]] = []
    halted = False
    stage_failures = 0

    for index, (stage_name, stage_fraction, default_latency_cap) in enumerate(STAGES):
        if stage_name in failures:
            error_rate = round(max_error_rate + 0.01, 4)
            latency_p95_ms = max_latency_p95_ms + 20 + _noise(seed, stage_name, "latency")
        else:
            error_rate = round(0.005 + (index * 0.003) + (_noise(seed, stage_name, "error") * 0.001), 4)
            latency_p95_ms = 85 + (index * 12) + _noise(seed, stage_name, "latency")

        within_thresholds = error_rate <= max_error_rate and latency_p95_ms <= max_latency_p95_ms
        promoted = (not halted) and within_thresholds
        stage_pass = (not halted) and within_thresholds
        auto_halt = not promoted
        if not promoted:
            halted = True
            stage_failures += 1

        stages.append(
            {
                "stage": stage_name,
                "fraction": stage_fraction,
                "blast_radius_budget_pct": int(stage_fraction * 100),
                "observed_error_rate": error_rate,
                "error_rate_threshold": max_error_rate,
                "observed_latency_p95_ms": latency_p95_ms,
                "latency_p95_ms_threshold": max_latency_p95_ms,
                "stage_latency_cap_ms": default_latency_cap,
                "promoted": promoted,
                "auto_halt": auto_halt,
                "rollback_recommended": auto_halt,
                "pass": stage_pass,
            }
        )

    checks = [
        {
            "name": "stages_defined",
            "pass": len(stages) == 3,
        },
        {
            "name": "canary_blast_radius_within_budget",
            "pass": stages[0]["blast_radius_budget_pct"] == 1,
        },
        {
            "name": "halt_triggered_on_first_failed_stage",
            "pass": all(
                not stage["promoted"]
                for stage in stages[
                    next(
                        (idx for idx, stage in enumerate(stages) if stage["pass"] is False),
                        len(stages),
                    ) :
                ]
            )
            if any(stage["pass"] is False for stage in stages)
            else True,
        },
    ]
    total_failures = stage_failures + sum(1 for check in checks if check["pass"] is False)

    return {
        "schema": SCHEMA,
        "policy_id": POLICY_ID,
        "slo_policy_id": SLO_POLICY_ID,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed": seed,
        "max_error_rate": max_error_rate,
        "max_latency_p95_ms": max_latency_p95_ms,
        "halted": halted,
        "stages": stages,
        "checks": checks,
        "total_failures": total_failures,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    p.add_argument("--max-error-rate", type=float, default=0.02)
    p.add_argument("--max-latency-p95-ms", type=int, default=120)
    p.add_argument("--inject-failure-stage", action="append", default=[])
    p.add_argument("--max-failures", type=int, default=0)
    p.add_argument("--out", default="out/canary-rollout-sim-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.max_failures < 0:
        print("error: max-failures must be >= 0")
        return 2
    if not (0.0 <= args.max_error_rate <= 1.0):
        print("error: max-error-rate must be in [0, 1]")
        return 2
    if args.max_latency_p95_ms <= 0:
        print("error: max-latency-p95-ms must be > 0")
        return 2

    try:
        injected_failure_stages = _parse_injected_failures(args.inject_failure_stage)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    report = run_sim(
        seed=args.seed,
        max_error_rate=args.max_error_rate,
        max_latency_p95_ms=args.max_latency_p95_ms,
        injected_failure_stages=injected_failure_stages,
    )
    report["max_failures"] = args.max_failures
    report["gate_pass"] = report["total_failures"] <= args.max_failures

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"canary-rollout-report: {out_path}")
    print(f"halted: {report['halted']}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
