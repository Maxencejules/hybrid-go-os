#!/usr/bin/env python3
"""Run deterministic fleet update orchestration simulation for M33."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple


SCHEMA = "rugo.fleet_update_sim_report.v1"
POLICY_ID = "rugo.fleet_update_policy.v1"
DEFAULT_SEED = 20260309
GROUPS: Sequence[Tuple[str, int, str]] = (
    ("canary", 24, "2.3.0"),
    ("batch_a", 180, "2.3.1"),
    ("batch_b", 796, "2.3.2"),
)


def _known_groups() -> Set[str]:
    return {group for group, _, _ in GROUPS}


def _parse_injected_failures(values: Sequence[str]) -> Set[str]:
    requested = {value.strip() for value in values if value.strip()}
    unknown = sorted(requested - _known_groups())
    if unknown:
        raise ValueError(f"unknown group ids in --inject-failure-group: {', '.join(unknown)}")
    return requested


def _noise(seed: int, group: str) -> int:
    digest = hashlib.sha256(f"{seed}|{group}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 5


def run_sim(
    seed: int,
    target_version: str,
    min_success_rate: float,
    injected_failure_groups: Set[str] | None = None,
) -> Dict[str, object]:
    failures = set() if injected_failure_groups is None else set(injected_failure_groups)
    groups: List[Dict[str, object]] = []
    stage_blocked = False
    group_failures = 0

    for index, (group_id, nodes_total, current_version) in enumerate(GROUPS):
        base_success = 0.992 - (0.002 * index) - (_noise(seed, group_id) * 0.0005)
        if group_id in failures:
            success_rate = round(max(0.0, min_success_rate - 0.03), 4)
        else:
            success_rate = round(min(1.0, max(base_success, min_success_rate)), 4)

        passes = success_rate >= min_success_rate
        promoted = (not stage_blocked) and passes
        rollback_triggered = (not passes) or stage_blocked
        nodes_updated = int(round(nodes_total * success_rate))

        if not passes:
            group_failures += 1
            stage_blocked = True
        elif stage_blocked:
            group_failures += 1

        groups.append(
            {
                "group_id": group_id,
                "current_version": current_version,
                "target_version": target_version,
                "nodes_total": nodes_total,
                "nodes_updated": nodes_updated,
                "success_rate": success_rate,
                "min_success_rate": min_success_rate,
                "promoted": promoted,
                "rollback_triggered": rollback_triggered,
                "pass": passes and not stage_blocked,
            }
        )

    checks = [
        {
            "name": "group_set_non_empty",
            "pass": len(groups) > 0,
        },
        {
            "name": "all_groups_meet_success_rate",
            "pass": all(entry["success_rate"] >= min_success_rate for entry in groups),
        },
        {
            "name": "promotion_stops_after_first_failure",
            "pass": all(
                (not groups[idx - 1]["rollback_triggered"]) or (not entry["promoted"])
                for idx, entry in enumerate(groups)
                if idx > 0
            ),
        },
    ]

    total_failures = group_failures + sum(1 for check in checks if check["pass"] is False)
    return {
        "schema": SCHEMA,
        "policy_id": POLICY_ID,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed": seed,
        "target_version": target_version,
        "groups": groups,
        "checks": checks,
        "total_failures": total_failures,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--target-version", default="2.4.0")
    parser.add_argument("--min-success-rate", type=float, default=0.98)
    parser.add_argument("--inject-failure-group", action="append", default=[])
    parser.add_argument("--max-failures", type=int, default=0)
    parser.add_argument("--out", default="out/fleet-update-sim-v1.json")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.max_failures < 0:
        print("error: max-failures must be >= 0")
        return 2
    if not (0.0 < args.min_success_rate <= 1.0):
        print("error: min-success-rate must be in (0, 1]")
        return 2

    try:
        injected_failure_groups = _parse_injected_failures(args.inject_failure_group)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    report = run_sim(
        seed=args.seed,
        target_version=args.target_version,
        min_success_rate=args.min_success_rate,
        injected_failure_groups=injected_failure_groups,
    )
    report["max_failures"] = args.max_failures
    report["gate_pass"] = report["total_failures"] <= args.max_failures

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"fleet-update-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
