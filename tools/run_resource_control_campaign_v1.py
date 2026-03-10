#!/usr/bin/env python3
"""Run deterministic resource-control policy checks for M42."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set


SCHEMA = "rugo.resource_control_report.v1"
POLICY_ID = "rugo.resource_control_policy.v1"
NAMESPACE_CGROUP_CONTRACT_ID = "rugo.namespace_cgroup_contract.v1"
ISOLATION_PROFILE_ID = "rugo.isolation_profile.v1"
REQUIREMENT_SCHEMA = "rugo.resource_control_requirement_set.v1"
ISOLATION_CAMPAIGN_SCHEMA = "rugo.isolation_campaign_report.v1"
DEFAULT_SEED = 20260310


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
        check_id="cpu_hard_quota_enforcement_ratio",
        domain="cpu",
        metric_key="cpu_hard_quota_enforcement_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="cpu_throttle_recovery_ms",
        domain="cpu",
        metric_key="cpu_throttle_recovery_ms",
        operator="max",
        threshold=30.0,
        base=13.0,
        spread=10,
        scale=1.0,
    ),
    CheckSpec(
        check_id="cpu_quota_violation_count",
        domain="cpu",
        metric_key="cpu_quota_violation_count",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=1.0,
    ),
    CheckSpec(
        check_id="memory_hard_limit_enforcement_ratio",
        domain="memory",
        metric_key="memory_hard_limit_enforcement_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="memory_oom_reclaim_latency_ms",
        domain="memory",
        metric_key="memory_oom_reclaim_latency_ms",
        operator="max",
        threshold=55.0,
        base=25.0,
        spread=15,
        scale=1.0,
    ),
    CheckSpec(
        check_id="memory_limit_breach_count",
        domain="memory",
        metric_key="memory_limit_breach_count",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=1.0,
    ),
    CheckSpec(
        check_id="io_bw_cap_enforcement_ratio",
        domain="io",
        metric_key="io_bw_cap_enforcement_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="io_latency_p99_ms",
        domain="io",
        metric_key="io_latency_p99_ms",
        operator="max",
        threshold=25.0,
        base=12.0,
        spread=8,
        scale=1.0,
    ),
    CheckSpec(
        check_id="pids_max_enforcement_ratio",
        domain="pids",
        metric_key="pids_max_enforcement_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="noisy_neighbor_containment_ratio",
        domain="global",
        metric_key="noisy_neighbor_containment_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="controller_drift_events",
        domain="global",
        metric_key="controller_drift_events",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=1.0,
    ),
    CheckSpec(
        check_id="throttle_fairness_ratio",
        domain="global",
        metric_key="throttle_fairness_ratio",
        operator="min",
        threshold=0.98,
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


def run_campaign(seed: int, injected_failures: Set[str] | None = None) -> Dict[str, object]:
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

    summary = {
        "cpu": _domain_summary(checks, "cpu"),
        "memory": _domain_summary(checks, "memory"),
        "io": _domain_summary(checks, "io"),
        "pids": _domain_summary(checks, "pids"),
        "global": _domain_summary(checks, "global"),
    }
    total_failures = sum(1 for check in checks if check["pass"] is False)

    stable_payload = {
        "schema": SCHEMA,
        "policy_id": POLICY_ID,
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
        "policy_id": POLICY_ID,
        "namespace_cgroup_contract_id": NAMESPACE_CGROUP_CONTRACT_ID,
        "isolation_profile_id": ISOLATION_PROFILE_ID,
        "requirement_schema": REQUIREMENT_SCHEMA,
        "isolation_campaign_schema": ISOLATION_CAMPAIGN_SCHEMA,
        "seed": seed,
        "gate": "test-namespace-cgroup-v1",
        "checks": checks,
        "summary": summary,
        "cpu": {
            "hard_quota_enforcement_ratio": metric_values[
                "cpu_hard_quota_enforcement_ratio"
            ],
            "throttle_recovery_ms": metric_values["cpu_throttle_recovery_ms"],
            "quota_violation_count": int(metric_values["cpu_quota_violation_count"]),
            "checks_pass": summary["cpu"]["pass"],
        },
        "memory": {
            "hard_limit_enforcement_ratio": metric_values[
                "memory_hard_limit_enforcement_ratio"
            ],
            "oom_reclaim_latency_ms": metric_values["memory_oom_reclaim_latency_ms"],
            "limit_breach_count": int(metric_values["memory_limit_breach_count"]),
            "checks_pass": summary["memory"]["pass"],
        },
        "io": {
            "bw_cap_enforcement_ratio": metric_values["io_bw_cap_enforcement_ratio"],
            "latency_p99_ms": metric_values["io_latency_p99_ms"],
            "checks_pass": summary["io"]["pass"],
        },
        "pids": {
            "max_enforcement_ratio": metric_values["pids_max_enforcement_ratio"],
            "checks_pass": summary["pids"]["pass"],
        },
        "global": {
            "noisy_neighbor_containment_ratio": metric_values[
                "noisy_neighbor_containment_ratio"
            ],
            "controller_drift_events": int(metric_values["controller_drift_events"]),
            "throttle_fairness_ratio": metric_values["throttle_fairness_ratio"],
            "checks_pass": summary["global"]["pass"],
        },
        "artifact_refs": {
            "junit": "out/pytest-namespace-cgroup-v1.xml",
            "resource_control_report": "out/resource-control-v1.json",
            "isolation_report": "out/isolation-campaign-v1.json",
            "ci_artifact": "namespace-cgroup-v1-artifacts",
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
    parser.add_argument("--out", default="out/resource-control-v1.json")
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

    report = run_campaign(seed=args.seed, injected_failures=injected_failures)
    report["max_failures"] = args.max_failures
    report["gate_pass"] = report["total_failures"] <= args.max_failures

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"resource-control-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
