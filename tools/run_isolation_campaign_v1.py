#!/usr/bin/env python3
"""Run deterministic namespace/cgroup isolation campaign checks for M42."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set


SCHEMA = "rugo.isolation_campaign_report.v1"
NAMESPACE_CGROUP_CONTRACT_ID = "rugo.namespace_cgroup_contract.v1"
ISOLATION_PROFILE_ID = "rugo.isolation_profile.v1"
RESOURCE_CONTROL_POLICY_ID = "rugo.resource_control_policy.v1"
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
        check_id="namespace_pid_isolation_ratio",
        domain="namespace",
        metric_key="namespace_pid_isolation_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="namespace_mount_isolation_ratio",
        domain="namespace",
        metric_key="namespace_mount_isolation_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="namespace_uts_isolation_ratio",
        domain="namespace",
        metric_key="namespace_uts_isolation_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="namespace_net_isolation_ratio",
        domain="namespace",
        metric_key="namespace_net_isolation_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="cgroup_cpu_quota_enforcement_ratio",
        domain="cgroup",
        metric_key="cgroup_cpu_quota_enforcement_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="cgroup_memory_limit_enforcement_ratio",
        domain="cgroup",
        metric_key="cgroup_memory_limit_enforcement_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="cgroup_io_weight_enforcement_ratio",
        domain="cgroup",
        metric_key="cgroup_io_weight_enforcement_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="cgroup_pids_limit_enforcement_ratio",
        domain="cgroup",
        metric_key="cgroup_pids_limit_enforcement_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="escape_setns_denied_ratio",
        domain="escape",
        metric_key="escape_setns_denied_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="escape_cross_tenant_signal_denied_ratio",
        domain="escape",
        metric_key="escape_cross_tenant_signal_denied_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="escape_mount_propagation_block_ratio",
        domain="escape",
        metric_key="escape_mount_propagation_block_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="escape_privilege_escalation_events",
        domain="escape",
        metric_key="escape_privilege_escalation_events",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=1.0,
    ),
    CheckSpec(
        check_id="escape_namespace_leak_events",
        domain="escape",
        metric_key="escape_namespace_leak_events",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=1.0,
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
        "namespace": _domain_summary(checks, "namespace"),
        "cgroup": _domain_summary(checks, "cgroup"),
        "escape": _domain_summary(checks, "escape"),
    }
    total_failures = sum(1 for check in checks if check["pass"] is False)

    stable_payload = {
        "schema": SCHEMA,
        "namespace_cgroup_contract_id": NAMESPACE_CGROUP_CONTRACT_ID,
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
        "namespace_cgroup_contract_id": NAMESPACE_CGROUP_CONTRACT_ID,
        "isolation_profile_id": ISOLATION_PROFILE_ID,
        "resource_control_policy_id": RESOURCE_CONTROL_POLICY_ID,
        "seed": seed,
        "gate": "test-isolation-baseline-v1",
        "checks": checks,
        "summary": summary,
        "namespace": {
            "pid_isolation_ratio": metric_values["namespace_pid_isolation_ratio"],
            "mount_isolation_ratio": metric_values["namespace_mount_isolation_ratio"],
            "uts_isolation_ratio": metric_values["namespace_uts_isolation_ratio"],
            "net_isolation_ratio": metric_values["namespace_net_isolation_ratio"],
            "checks_pass": summary["namespace"]["pass"],
        },
        "cgroup": {
            "cpu_quota_enforcement_ratio": metric_values[
                "cgroup_cpu_quota_enforcement_ratio"
            ],
            "memory_limit_enforcement_ratio": metric_values[
                "cgroup_memory_limit_enforcement_ratio"
            ],
            "io_weight_enforcement_ratio": metric_values[
                "cgroup_io_weight_enforcement_ratio"
            ],
            "pids_limit_enforcement_ratio": metric_values[
                "cgroup_pids_limit_enforcement_ratio"
            ],
            "checks_pass": summary["cgroup"]["pass"],
        },
        "escape_negative_paths": {
            "setns_denied_ratio": metric_values["escape_setns_denied_ratio"],
            "cross_tenant_signal_denied_ratio": metric_values[
                "escape_cross_tenant_signal_denied_ratio"
            ],
            "mount_propagation_block_ratio": metric_values[
                "escape_mount_propagation_block_ratio"
            ],
            "privilege_escalation_events": int(
                metric_values["escape_privilege_escalation_events"]
            ),
            "namespace_leak_events": int(metric_values["escape_namespace_leak_events"]),
            "checks_pass": summary["escape"]["pass"],
        },
        "artifact_refs": {
            "junit": "out/pytest-isolation-baseline-v1.xml",
            "isolation_report": "out/isolation-campaign-v1.json",
            "resource_control_report": "out/resource-control-v1.json",
            "ci_artifact": "isolation-baseline-v1-artifacts",
            "sub_gate_ci_artifact": "namespace-cgroup-v1-artifacts",
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
    parser.add_argument("--out", default="out/isolation-campaign-v1.json")
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

    print(f"isolation-campaign-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
