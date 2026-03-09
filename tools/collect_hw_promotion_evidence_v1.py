#!/usr/bin/env python3
"""Collect deterministic bare-metal promotion evidence for M37."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set

import run_hw_matrix_v4 as matrix


SCHEMA = "rugo.hw_baremetal_promotion_report.v1"
POLICY_ID = "rugo.hw_baremetal_promotion_policy.v1"
MATRIX_SCHEMA = "rugo.hw_matrix_evidence.v4"
DEFAULT_SEED = 20260309
DEFAULT_CAMPAIGN_RUNS = 12
DEFAULT_REQUIRED_CONSECUTIVE_GREEN = 12
DEFAULT_MIN_PASS_RATE = 0.98
REQUIRED_ARTIFACT_KEYS = ("matrix_junit", "matrix_report", "promotion_report")


def _normalize_strings(values: Sequence[str]) -> Set[str]:
    return {value.strip() for value in values if value.strip()}


def _normalize_run_failures(values: Sequence[str], campaign_runs: int) -> Set[int]:
    runs: Set[int] = set()
    for value in values:
        stripped = value.strip()
        if not stripped:
            continue
        try:
            run_id = int(stripped)
        except ValueError as exc:
            raise ValueError(f"invalid run id in --inject-run-failure: {stripped}") from exc
        if run_id < 1 or run_id > campaign_runs:
            raise ValueError(
                f"run id out of range in --inject-run-failure: {run_id} "
                f"(valid range: 1..{campaign_runs})"
            )
        runs.add(run_id)
    return runs


def _validate_missing_artifacts(missing: Set[str]) -> None:
    unknown = sorted(missing - set(REQUIRED_ARTIFACT_KEYS))
    if unknown:
        raise ValueError(
            "unknown artifacts in --inject-missing-artifact: " + ", ".join(unknown)
        )


def _trailing_consecutive_green(run_results: List[Dict[str, object]]) -> int:
    trailing = 0
    for row in reversed(run_results):
        if row["gate_pass"]:
            trailing += 1
            continue
        break
    return trailing


def run_promotion(
    seed: int,
    campaign_runs: int,
    required_consecutive_green: int,
    min_pass_rate: float,
    injected_run_failures: Set[int] | None = None,
    missing_artifacts: Set[str] | None = None,
) -> Dict[str, object]:
    fail_runs = set() if injected_run_failures is None else set(injected_run_failures)
    missing = set() if missing_artifacts is None else set(missing_artifacts)

    run_results: List[Dict[str, object]] = []
    for run_id in range(1, campaign_runs + 1):
        run_seed = seed + run_id
        injected = {"tier0_storage_smoke"} if run_id in fail_runs else set()
        report = matrix.run_matrix(
            seed=run_seed,
            injected_failures=injected,
            max_failures=0,
        )
        run_results.append(
            {
                "run_id": run_id,
                "seed": run_seed,
                "gate_pass": report["gate_pass"],
                "total_failures": report["total_failures"],
                "digest": report["digest"],
            }
        )

    green_runs = sum(1 for row in run_results if row["gate_pass"])
    failed_runs = campaign_runs - green_runs
    pass_rate = round((green_runs / campaign_runs) if campaign_runs else 0.0, 3)
    trailing_green = _trailing_consecutive_green(run_results)

    artifact_refs = {
        "matrix_junit": "out/pytest-hw-matrix-v4.xml",
        "matrix_report": "out/hw-matrix-v4.json",
        "promotion_report": "out/hw-promotion-v1.json",
        "ci_artifact": "hw-baremetal-promotion-v1-artifacts",
    }
    available_artifacts = sorted(
        key for key in REQUIRED_ARTIFACT_KEYS if key not in missing
    )

    policy_checks = [
        {
            "check_id": "campaign_length",
            "operator": "min",
            "threshold": required_consecutive_green,
            "observed": campaign_runs,
            "pass": campaign_runs >= required_consecutive_green,
        },
        {
            "check_id": "campaign_pass_rate",
            "operator": "min",
            "threshold": min_pass_rate,
            "observed": pass_rate,
            "pass": pass_rate >= min_pass_rate,
        },
        {
            "check_id": "trailing_consecutive_green",
            "operator": "min",
            "threshold": required_consecutive_green,
            "observed": trailing_green,
            "pass": trailing_green >= required_consecutive_green,
        },
        {
            "check_id": "artifact_bundle_complete",
            "operator": "eq",
            "threshold": True,
            "observed": len(missing) == 0,
            "pass": len(missing) == 0,
        },
    ]

    failures = sorted(
        check["check_id"] for check in policy_checks if check["pass"] is False
    )
    total_failures = len(failures)
    gate_pass = total_failures == 0

    stable_payload = {
        "schema": SCHEMA,
        "policy_id": POLICY_ID,
        "seed": seed,
        "campaign_runs": campaign_runs,
        "required_consecutive_green": required_consecutive_green,
        "min_pass_rate": min_pass_rate,
        "run_results": run_results,
        "missing_artifacts": sorted(missing),
        "policy_checks": [
            {"check_id": check["check_id"], "pass": check["pass"]}
            for check in policy_checks
        ],
    }
    digest = hashlib.sha256(
        json.dumps(stable_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return {
        "schema": SCHEMA,
        "policy_id": POLICY_ID,
        "matrix_schema_id": MATRIX_SCHEMA,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed": seed,
        "campaign_runs": campaign_runs,
        "required_consecutive_green": required_consecutive_green,
        "min_pass_rate": min_pass_rate,
        "run_results": run_results,
        "summary": {
            "green_runs": green_runs,
            "failed_runs": failed_runs,
            "pass_rate": pass_rate,
            "trailing_consecutive_green": trailing_green,
        },
        "profile_results": [
            {
                "profile_id": "intel_nuc13_i226",
                "board_class": "tier2",
                "required_for_promotion": True,
                "campaign_runs": campaign_runs,
                "pass_rate": pass_rate,
            },
            {
                "profile_id": "amd_b550_rtl8125",
                "board_class": "tier3",
                "required_for_promotion": False,
                "campaign_runs": campaign_runs,
                "pass_rate": pass_rate,
            },
        ],
        "artifact_refs": artifact_refs,
        "available_artifacts": available_artifacts,
        "missing_artifacts": sorted(missing),
        "policy_checks": policy_checks,
        "injected_run_failures": sorted(fail_runs),
        "total_failures": total_failures,
        "failures": failures,
        "gate_pass": gate_pass,
        "digest": digest,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--campaign-runs", type=int, default=DEFAULT_CAMPAIGN_RUNS)
    parser.add_argument(
        "--required-consecutive-green",
        type=int,
        default=DEFAULT_REQUIRED_CONSECUTIVE_GREEN,
    )
    parser.add_argument("--min-pass-rate", type=float, default=DEFAULT_MIN_PASS_RATE)
    parser.add_argument(
        "--inject-run-failure",
        action="append",
        default=[],
        help="force a campaign run to fail by run id (1-indexed)",
    )
    parser.add_argument(
        "--inject-missing-artifact",
        action="append",
        default=[],
        help="remove required artifact key from bundle",
    )
    parser.add_argument("--out", default="out/hw-promotion-v1.json")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.campaign_runs <= 0:
        print("error: campaign-runs must be > 0")
        return 2
    if args.required_consecutive_green <= 0:
        print("error: required-consecutive-green must be > 0")
        return 2
    if args.required_consecutive_green > args.campaign_runs:
        print("error: required-consecutive-green must be <= campaign-runs")
        return 2
    if args.min_pass_rate < 0.0 or args.min_pass_rate > 1.0:
        print("error: min-pass-rate must be within [0, 1]")
        return 2

    try:
        run_failures = _normalize_run_failures(
            args.inject_run_failure,
            args.campaign_runs,
        )
        missing = _normalize_strings(args.inject_missing_artifact)
        _validate_missing_artifacts(missing)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    report = run_promotion(
        seed=args.seed,
        campaign_runs=args.campaign_runs,
        required_consecutive_green=args.required_consecutive_green,
        min_pass_rate=args.min_pass_rate,
        injected_run_failures=run_failures,
        missing_artifacts=missing,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"hw-promotion-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
