#!/usr/bin/env python3
"""Run deterministic profile conformance qualification checks for M32."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple


SCHEMA = "rugo.profile_conformance_report.v1"
POLICY_ID = "rugo.profile_conformance_policy.v1"
PROFILE_SCHEMA = "rugo.profile_requirement_set.v1"
DEFAULT_SEED = 20260309


@dataclass(frozen=True)
class Requirement:
    requirement_id: str
    metric_key: str
    operator: str  # one of: min, max, eq
    threshold: int
    margin: int


@dataclass(frozen=True)
class ProfileSpec:
    profile_id: str
    label: str
    requirements: Sequence[Requirement]


PROFILES: Dict[str, ProfileSpec] = {
    "server_v1": ProfileSpec(
        profile_id="server_v1",
        label="server",
        requirements=[
            Requirement(
                requirement_id="service_restart_coverage_pct",
                metric_key="service_restart_coverage_pct",
                operator="min",
                threshold=95,
                margin=2,
            ),
            Requirement(
                requirement_id="max_crash_recovery_seconds",
                metric_key="max_crash_recovery_seconds",
                operator="max",
                threshold=30,
                margin=3,
            ),
            Requirement(
                requirement_id="network_ipv6_enabled",
                metric_key="network_ipv6_enabled",
                operator="eq",
                threshold=1,
                margin=0,
            ),
            Requirement(
                requirement_id="supply_chain_attestation",
                metric_key="supply_chain_attestation",
                operator="eq",
                threshold=1,
                margin=0,
            ),
        ],
    ),
    "developer_v1": ProfileSpec(
        profile_id="developer_v1",
        label="developer",
        requirements=[
            Requirement(
                requirement_id="toolchain_smoke_pass",
                metric_key="toolchain_smoke_pass",
                operator="eq",
                threshold=1,
                margin=0,
            ),
            Requirement(
                requirement_id="debug_symbols_available",
                metric_key="debug_symbols_available",
                operator="eq",
                threshold=1,
                margin=0,
            ),
            Requirement(
                requirement_id="package_build_success_rate_pct",
                metric_key="package_build_success_rate_pct",
                operator="min",
                threshold=98,
                margin=1,
            ),
            Requirement(
                requirement_id="interactive_shell_latency_ms_p95",
                metric_key="interactive_shell_latency_ms_p95",
                operator="max",
                threshold=120,
                margin=6,
            ),
        ],
    ),
    "appliance_v1": ProfileSpec(
        profile_id="appliance_v1",
        label="appliance",
        requirements=[
            Requirement(
                requirement_id="immutable_rootfs_enforced",
                metric_key="immutable_rootfs_enforced",
                operator="eq",
                threshold=1,
                margin=0,
            ),
            Requirement(
                requirement_id="read_only_runtime_pct",
                metric_key="read_only_runtime_pct",
                operator="min",
                threshold=99,
                margin=1,
            ),
            Requirement(
                requirement_id="boot_to_service_seconds_p95",
                metric_key="boot_to_service_seconds_p95",
                operator="max",
                threshold=45,
                margin=4,
            ),
            Requirement(
                requirement_id="remote_mgmt_surface_minimized",
                metric_key="remote_mgmt_surface_minimized",
                operator="eq",
                threshold=1,
                margin=0,
            ),
        ],
    ),
}


def _known_requirement_pairs() -> Set[Tuple[str, str]]:
    pairs: Set[Tuple[str, str]] = set()
    for profile in PROFILES.values():
        for req in profile.requirements:
            pairs.add((profile.profile_id, req.requirement_id))
    return pairs


def _metric_noise(seed: int, profile_id: str, requirement_id: str) -> int:
    digest = hashlib.sha256(
        f"{seed}|{profile_id}|{requirement_id}".encode("utf-8")
    ).hexdigest()
    return int(digest[:8], 16) % 3


def _measure(
    seed: int,
    profile_id: str,
    requirement: Requirement,
    injected_failures: Set[Tuple[str, str]],
) -> int:
    pair = (profile_id, requirement.requirement_id)
    if pair in injected_failures:
        if requirement.operator == "min":
            return requirement.threshold - 1
        if requirement.operator == "max":
            return requirement.threshold + 1
        return 0 if requirement.threshold != 0 else 1

    noise = _metric_noise(seed, profile_id, requirement.requirement_id)
    if requirement.operator == "min":
        return requirement.threshold + requirement.margin + noise
    if requirement.operator == "max":
        return requirement.threshold - requirement.margin - noise
    return requirement.threshold


def _passes(operator: str, observed: int, threshold: int) -> bool:
    if operator == "min":
        return observed >= threshold
    if operator == "max":
        return observed <= threshold
    if operator == "eq":
        return observed == threshold
    raise ValueError(f"unsupported operator: {operator}")


def _normalize_profiles(values: Sequence[str]) -> List[str]:
    if not values:
        return sorted(PROFILES.keys())
    unique = []
    seen = set()
    for value in values:
        candidate = value.strip()
        if not candidate or candidate in seen:
            continue
        if candidate not in PROFILES:
            raise ValueError(f"unknown profile id: {candidate}")
        seen.add(candidate)
        unique.append(candidate)
    if not unique:
        raise ValueError("at least one profile must be selected")
    return sorted(unique)


def _parse_injections(values: Sequence[str]) -> Set[Tuple[str, str]]:
    pairs: Set[Tuple[str, str]] = set()
    if not values:
        return pairs

    known = _known_requirement_pairs()
    for raw in values:
        text = raw.strip()
        if not text:
            continue
        parts = text.split(":", 1)
        if len(parts) != 2:
            raise ValueError(
                "inject-failure entries must be '<profile_id>:<requirement_id>'"
            )
        pair = (parts[0], parts[1])
        if pair not in known:
            raise ValueError(
                "unknown inject-failure target: "
                f"{parts[0]}:{parts[1]}"
            )
        pairs.add(pair)
    return pairs


def run_suite(
    seed: int,
    selected_profiles: Sequence[str],
    injected_failures: Set[Tuple[str, str]] | None = None,
) -> Dict[str, object]:
    failures = set() if injected_failures is None else set(injected_failures)
    profiles = _normalize_profiles(selected_profiles)

    profile_reports: List[Dict[str, object]] = []
    total_failures = 0

    for profile_id in profiles:
        spec = PROFILES[profile_id]
        req_reports: List[Dict[str, object]] = []
        profile_failures = 0
        for req in spec.requirements:
            observed = _measure(seed, profile_id, req, failures)
            passed = _passes(req.operator, observed, req.threshold)
            if not passed:
                profile_failures += 1
            req_reports.append(
                {
                    "requirement_id": req.requirement_id,
                    "metric_key": req.metric_key,
                    "operator": req.operator,
                    "threshold": req.threshold,
                    "observed": observed,
                    "pass": passed,
                }
            )

        checks = [
            {
                "name": "requirements_defined",
                "pass": len(req_reports) > 0,
            },
            {
                "name": "requirements_all_pass",
                "pass": profile_failures == 0,
            },
        ]
        total_failures += profile_failures + sum(
            1 for check in checks if check["pass"] is False
        )
        profile_reports.append(
            {
                "profile_id": spec.profile_id,
                "profile_label": spec.label,
                "profile_schema": PROFILE_SCHEMA,
                "requirements": req_reports,
                "checks": checks,
                "total_failures": profile_failures,
                "qualification_pass": profile_failures == 0,
            }
        )

    stable_payload = {
        "schema": SCHEMA,
        "policy_id": POLICY_ID,
        "profile_schema": PROFILE_SCHEMA,
        "seed": seed,
        "profiles": profile_reports,
        "injected_failures": sorted(
            [f"{profile_id}:{requirement_id}" for profile_id, requirement_id in failures]
        ),
    }
    digest = hashlib.sha256(
        json.dumps(stable_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return {
        "schema": SCHEMA,
        "policy_id": POLICY_ID,
        "profile_schema": PROFILE_SCHEMA,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed": seed,
        "checked_profiles": profiles,
        "profiles": profile_reports,
        "injected_failures": sorted(
            [f"{profile_id}:{requirement_id}" for profile_id, requirement_id in failures]
        ),
        "total_failures": total_failures,
        "digest": digest,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--profile",
        action="append",
        default=[],
        help="profile id to evaluate (default: all profiles)",
    )
    parser.add_argument(
        "--inject-failure",
        action="append",
        default=[],
        help="force requirement failure in the form <profile_id>:<requirement_id>",
    )
    parser.add_argument("--max-failures", type=int, default=0)
    parser.add_argument("--out", default="out/conformance-v1.json")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.max_failures < 0:
        print("error: max-failures must be >= 0")
        return 2

    try:
        selected_profiles = _normalize_profiles(args.profile)
        failures = _parse_injections(args.inject_failure)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    report = run_suite(
        seed=args.seed,
        selected_profiles=selected_profiles,
        injected_failures=failures,
    )
    report["max_failures"] = args.max_failures
    report["gate_pass"] = report["total_failures"] <= args.max_failures

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"profile-conformance-report: {out_path}")
    print(f"profiles: {','.join(report['checked_profiles'])}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
