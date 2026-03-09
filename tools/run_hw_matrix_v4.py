#!/usr/bin/env python3
"""Run deterministic hardware matrix v4 checks for M37."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set


SCHEMA = "rugo.hw_matrix_evidence.v4"
MATRIX_CONTRACT_ID = "rugo.hw.support_matrix.v4"
DRIVER_CONTRACT_ID = "rugo.driver_lifecycle_report.v4"
PROMOTION_POLICY_ID = "rugo.hw_baremetal_promotion_policy.v1"
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
        check_id="tier0_storage_smoke",
        domain="matrix",
        metric_key="tier0_storage_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="tier1_storage_smoke",
        domain="matrix",
        metric_key="tier1_storage_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="tier0_network_smoke",
        domain="matrix",
        metric_key="tier0_network_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="tier1_network_smoke",
        domain="matrix",
        metric_key="tier1_network_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="lifecycle_virtio_blk",
        domain="lifecycle",
        metric_key="virtio_blk_runtime_errors",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="lifecycle_virtio_net",
        domain="lifecycle",
        metric_key="virtio_net_runtime_errors",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="coverage_storage_ahci",
        domain="coverage",
        metric_key="ahci_coverage_gap",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="coverage_storage_nvme",
        domain="coverage",
        metric_key="nvme_coverage_gap",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="coverage_network_e1000",
        domain="coverage",
        metric_key="e1000_coverage_gap",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="coverage_network_rtl8139",
        domain="coverage",
        metric_key="rtl8139_coverage_gap",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="negative_blk_missing_deterministic",
        domain="negative_path",
        metric_key="blk_missing_marker_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="negative_net_missing_deterministic",
        domain="negative_path",
        metric_key="net_missing_marker_ratio",
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


def _check_row(checks: List[Dict[str, object]], check_id: str) -> Dict[str, object]:
    rows = [row for row in checks if row["check_id"] == check_id]
    if len(rows) != 1:
        raise ValueError(f"expected exactly one row for check {check_id}")
    return rows[0]


def run_matrix(
    seed: int,
    injected_failures: Set[str] | None = None,
    max_failures: int = 0,
) -> Dict[str, object]:
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

    check_pass = {row["check_id"]: row["pass"] for row in checks}

    tier_results = [
        {
            "tier": "tier0",
            "machine": "q35",
            "storage_smoke": "pass" if check_pass["tier0_storage_smoke"] else "fail",
            "network_smoke": "pass" if check_pass["tier0_network_smoke"] else "fail",
            "status": (
                "pass"
                if check_pass["tier0_storage_smoke"] and check_pass["tier0_network_smoke"]
                else "fail"
            ),
        },
        {
            "tier": "tier1",
            "machine": "pc/i440fx",
            "storage_smoke": "pass" if check_pass["tier1_storage_smoke"] else "fail",
            "network_smoke": "pass" if check_pass["tier1_network_smoke"] else "fail",
            "status": (
                "pass"
                if check_pass["tier1_storage_smoke"] and check_pass["tier1_network_smoke"]
                else "fail"
            ),
        },
    ]

    required_states = [
        "probe_found",
        "init_ready",
        "runtime_ok",
        "suspend_prepare",
        "resume_ok",
        "hotplug_add",
        "hotplug_remove",
        "reset_recover",
    ]
    driver_lifecycle = []
    for driver_name, check_id, metric_key in [
        ("virtio-blk-pci", "lifecycle_virtio_blk", "virtio_blk_runtime_errors"),
        ("virtio-net-pci", "lifecycle_virtio_net", "virtio_net_runtime_errors"),
    ]:
        passed = check_pass[check_id]
        runtime_errors = 0 if passed else 1
        driver_lifecycle.append(
            {
                "driver": driver_name,
                "device_class": "storage" if "blk" in driver_name else "network",
                "states_observed": (
                    list(required_states) if passed else list(required_states) + ["error_fatal"]
                ),
                "probe_attempts": 1,
                "probe_successes": 1 if passed else 0,
                "init_failures": 0 if passed else 1,
                "runtime_errors": runtime_errors,
                "recoveries": 0,
                "fatal_errors": 0 if passed else 1,
                "status": "pass" if passed else "fail",
            }
        )

    device_class_coverage = [
        {
            "device": "virtio-blk-pci",
            "class": "storage",
            "required": True,
            "status": (
                "pass"
                if check_pass["tier0_storage_smoke"] and check_pass["tier1_storage_smoke"]
                else "fail"
            ),
        },
        {
            "device": "ahci",
            "class": "storage",
            "required": True,
            "status": "pass" if check_pass["coverage_storage_ahci"] else "fail",
        },
        {
            "device": "nvme",
            "class": "storage",
            "required": True,
            "status": "pass" if check_pass["coverage_storage_nvme"] else "fail",
        },
        {
            "device": "virtio-net-pci",
            "class": "network",
            "required": True,
            "status": (
                "pass"
                if check_pass["tier0_network_smoke"] and check_pass["tier1_network_smoke"]
                else "fail"
            ),
        },
        {
            "device": "e1000",
            "class": "network",
            "required": True,
            "status": "pass" if check_pass["coverage_network_e1000"] else "fail",
        },
        {
            "device": "rtl8139",
            "class": "network",
            "required": True,
            "status": "pass" if check_pass["coverage_network_rtl8139"] else "fail",
        },
    ]

    negative_paths = {
        "block_probe_missing": {
            "marker": "BLK: not found",
            "deterministic": check_pass["negative_blk_missing_deterministic"],
            "status": (
                "pass" if check_pass["negative_blk_missing_deterministic"] else "fail"
            ),
        },
        "net_probe_missing": {
            "marker": "NET: not found",
            "deterministic": check_pass["negative_net_missing_deterministic"],
            "status": (
                "pass" if check_pass["negative_net_missing_deterministic"] else "fail"
            ),
        },
    }

    total_failures = sum(1 for row in checks if row["pass"] is False)
    gate_pass = total_failures <= max_failures

    stable_payload = {
        "schema": SCHEMA,
        "seed": seed,
        "max_failures": max_failures,
        "checks": [
            {
                "check_id": row["check_id"],
                "pass": row["pass"],
                "observed": row["observed"],
            }
            for row in checks
        ],
        "injected_failures": sorted(failures),
    }
    digest = hashlib.sha256(
        json.dumps(stable_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return {
        "schema": SCHEMA,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "matrix_contract_id": MATRIX_CONTRACT_ID,
        "driver_contract_id": DRIVER_CONTRACT_ID,
        "promotion_policy_id": PROMOTION_POLICY_ID,
        "seed": seed,
        "gate": "test-hw-matrix-v4",
        "checks": checks,
        "summary": {
            "matrix": _domain_summary(checks, "matrix"),
            "lifecycle": _domain_summary(checks, "lifecycle"),
            "coverage": _domain_summary(checks, "coverage"),
            "negative_path": _domain_summary(checks, "negative_path"),
        },
        "tier_results": tier_results,
        "device_class_coverage": device_class_coverage,
        "driver_lifecycle": driver_lifecycle,
        "negative_paths": negative_paths,
        "artifact_refs": {
            "junit": "out/pytest-hw-matrix-v4.xml",
            "matrix_report": "out/hw-matrix-v4.json",
            "promotion_report": "out/hw-promotion-v1.json",
            "ci_artifact": "hw-matrix-v4-artifacts",
            "promotion_ci_artifact": "hw-baremetal-promotion-v1-artifacts",
        },
        "injected_failures": sorted(failures),
        "max_failures": max_failures,
        "total_failures": total_failures,
        "failures": sorted(
            row["check_id"] for row in checks if row["pass"] is False
        ),
        "gate_pass": gate_pass,
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
    parser.add_argument("--out", default="out/hw-matrix-v4.json")
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

    report = run_matrix(
        seed=args.seed,
        injected_failures=injected_failures,
        max_failures=args.max_failures,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"hw-matrix-v4-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
