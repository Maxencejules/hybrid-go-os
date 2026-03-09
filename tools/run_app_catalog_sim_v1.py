#!/usr/bin/env python3
"""Run deterministic app catalog scale simulation checks for M39."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set


SCHEMA = "rugo.app_catalog_sim_report.v1"
ECOSYSTEM_POLICY_ID = "rugo.ecosystem_scale_policy.v1"
CATALOG_QUALITY_CONTRACT_ID = "rugo.catalog_quality_contract.v1"
DISTRIBUTION_WORKFLOW_ID = "rugo.distribution_workflow.v1"
DEFAULT_SEED = 20260309


@dataclass(frozen=True)
class CheckSpec:
    check_id: str
    domain: str
    metric_key: str
    operator: str  # one of: min, max, eq
    threshold: float
    base: float
    spread: int
    scale: float


CHECKS: Sequence[CheckSpec] = (
    CheckSpec(
        check_id="catalog_total_entries",
        domain="coverage",
        metric_key="catalog_total_entries",
        operator="min",
        threshold=420.0,
        base=456.0,
        spread=28,
        scale=1.0,
    ),
    CheckSpec(
        check_id="productivity_entries",
        domain="coverage",
        metric_key="productivity_entries",
        operator="min",
        threshold=120.0,
        base=136.0,
        spread=18,
        scale=1.0,
    ),
    CheckSpec(
        check_id="devtools_entries",
        domain="coverage",
        metric_key="devtools_entries",
        operator="min",
        threshold=90.0,
        base=108.0,
        spread=16,
        scale=1.0,
    ),
    CheckSpec(
        check_id="media_entries",
        domain="coverage",
        metric_key="media_entries",
        operator="min",
        threshold=70.0,
        base=82.0,
        spread=10,
        scale=1.0,
    ),
    CheckSpec(
        check_id="utility_entries",
        domain="coverage",
        metric_key="utility_entries",
        operator="min",
        threshold=140.0,
        base=164.0,
        spread=20,
        scale=1.0,
    ),
    CheckSpec(
        check_id="metadata_completeness_ratio",
        domain="quality",
        metric_key="metadata_completeness_ratio",
        operator="min",
        threshold=0.995,
        base=0.997,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="signed_provenance_ratio",
        domain="quality",
        metric_key="signed_provenance_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="unsupported_workload_ratio",
        domain="quality",
        metric_key="unsupported_workload_ratio",
        operator="max",
        threshold=0.02,
        base=0.012,
        spread=4,
        scale=0.001,
    ),
    CheckSpec(
        check_id="policy_violation_count",
        domain="quality",
        metric_key="policy_violation_count",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="index_rebuild_determinism_ratio",
        domain="reproducibility",
        metric_key="index_rebuild_determinism_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
)


def _known_checks() -> Set[str]:
    return {spec.check_id for spec in CHECKS}


def _noise(seed: int, key: str) -> int:
    digest = hashlib.sha256(f"{seed}|{key}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _round_value(value: float) -> float:
    return round(value, 3)


def _baseline_observed(seed: int, spec: CheckSpec) -> float:
    spread = spec.spread if spec.spread > 0 else 1
    value = spec.base + ((_noise(seed, spec.check_id) % spread) * spec.scale)
    return _round_value(value)


def _failing_observed(spec: CheckSpec) -> float:
    delta = 0.001 if spec.scale < 1.0 else 1.0
    if spec.operator == "max":
        return _round_value(spec.threshold + delta)
    if spec.operator == "min":
        return _round_value(spec.threshold - delta)
    return _round_value(spec.threshold + delta)


def _passes(operator: str, observed: float, threshold: float) -> bool:
    if operator == "max":
        return observed <= threshold
    if operator == "min":
        return observed >= threshold
    if operator == "eq":
        return observed == threshold
    raise ValueError(f"unsupported operator: {operator}")


def _domain_summary(checks: List[Dict[str, object]], domain: str) -> Dict[str, object]:
    scoped = [entry for entry in checks if entry["domain"] == domain]
    failures = [entry for entry in scoped if entry["pass"] is False]
    return {
        "checks": len(scoped),
        "failures": len(failures),
        "pass": len(failures) == 0,
    }


def _normalize_failures(values: Sequence[str]) -> Set[str]:
    failures = {value.strip() for value in values if value.strip()}
    unknown = sorted(failures - _known_checks())
    if unknown:
        raise ValueError(f"unknown check ids in --inject-failure: {', '.join(unknown)}")
    return failures


def run_simulation(seed: int, injected_failures: Set[str] | None = None) -> Dict[str, object]:
    failures = set() if injected_failures is None else set(injected_failures)

    checks: List[Dict[str, object]] = []
    metric_values: Dict[str, float] = {}
    for spec in CHECKS:
        observed = (
            _failing_observed(spec)
            if spec.check_id in failures
            else _baseline_observed(seed, spec)
        )
        passed = _passes(spec.operator, observed, spec.threshold)
        checks.append(
            {
                "check_id": spec.check_id,
                "domain": spec.domain,
                "metric_key": spec.metric_key,
                "operator": spec.operator,
                "threshold": spec.threshold,
                "observed": observed,
                "pass": passed,
            }
        )
        metric_values[spec.metric_key] = observed

    total_failures = sum(1 for check in checks if check["pass"] is False)
    summary = {
        "coverage": _domain_summary(checks, "coverage"),
        "quality": _domain_summary(checks, "quality"),
        "reproducibility": _domain_summary(checks, "reproducibility"),
    }
    class_counts = {
        "productivity": int(metric_values["productivity_entries"]),
        "devtools": int(metric_values["devtools_entries"]),
        "media": int(metric_values["media_entries"]),
        "utility": int(metric_values["utility_entries"]),
    }

    stable_payload = {
        "schema": SCHEMA,
        "ecosystem_policy_id": ECOSYSTEM_POLICY_ID,
        "seed": seed,
        "checks": [
            {
                "check_id": check["check_id"],
                "pass": check["pass"],
                "observed": check["observed"],
            }
            for check in checks
        ],
        "injected_failures": sorted(failures),
    }
    digest = hashlib.sha256(
        json.dumps(stable_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return {
        "schema": SCHEMA,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ecosystem_policy_id": ECOSYSTEM_POLICY_ID,
        "catalog_quality_contract_id": CATALOG_QUALITY_CONTRACT_ID,
        "distribution_workflow_id": DISTRIBUTION_WORKFLOW_ID,
        "seed": seed,
        "gate": "test-ecosystem-scale-v1",
        "checks": checks,
        "summary": summary,
        "catalog": {
            "catalog_total_entries": int(metric_values["catalog_total_entries"]),
            "class_counts": class_counts,
            "checks_pass": summary["coverage"]["pass"],
        },
        "quality": {
            "metadata_completeness_ratio": metric_values["metadata_completeness_ratio"],
            "signed_provenance_ratio": metric_values["signed_provenance_ratio"],
            "unsupported_workload_ratio": metric_values["unsupported_workload_ratio"],
            "policy_violation_count": int(metric_values["policy_violation_count"]),
            "checks_pass": summary["quality"]["pass"],
        },
        "reproducibility": {
            "index_rebuild_determinism_ratio": metric_values[
                "index_rebuild_determinism_ratio"
            ],
            "checks_pass": summary["reproducibility"]["pass"],
        },
        "artifact_refs": {
            "junit": "out/pytest-ecosystem-scale-v1.xml",
            "catalog_report": "out/app-catalog-sim-v1.json",
            "install_report": "out/pkg-install-success-v1.json",
            "audit_report": "out/catalog-audit-v1.json",
            "ci_artifact": "ecosystem-scale-v1-artifacts",
            "health_ci_artifact": "app-catalog-health-v1-artifacts",
        },
        "injected_failures": sorted(failures),
        "total_failures": total_failures,
        "failures": sorted(
            check["check_id"] for check in checks if check["pass"] is False
        ),
        "digest": digest,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--inject-failure",
        action="append",
        default=[],
        help="force a check to fail by check_id",
    )
    parser.add_argument("--max-failures", type=int, default=0)
    parser.add_argument("--out", default="out/app-catalog-sim-v1.json")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.max_failures < 0:
        print("error: max-failures must be >= 0")
        return 2

    try:
        injected_failures = _normalize_failures(args.inject_failure)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    report = run_simulation(seed=args.seed, injected_failures=injected_failures)
    report["max_failures"] = args.max_failures
    report["gate_pass"] = report["total_failures"] <= args.max_failures

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"app-catalog-sim-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
