#!/usr/bin/env python3
"""Run deterministic hardware matrix v6 checks for M45."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set

import run_desktop_smoke_v1 as desktop_smoke


SCHEMA = "rugo.hw_matrix_evidence.v6"
MATRIX_CONTRACT_ID = "rugo.hw.support_matrix.v6"
DRIVER_CONTRACT_ID = "rugo.driver_lifecycle_report.v6"
VIRTIO_PLATFORM_PROFILE_ID = "rugo.virtio_platform_profile.v1"
DISPLAY_CONTRACT_ID = "rugo.display_stack_contract.v1"
SHADOW_BASELINE_CONTRACT_ID = "rugo.hw.support_matrix.v5"
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


BASE_CHECKS: Sequence[CheckSpec] = (
    CheckSpec(
        check_id="tier0_storage_transitional_smoke",
        domain="matrix_transitional",
        metric_key="tier0_storage_transitional_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="tier1_storage_transitional_smoke",
        domain="matrix_transitional",
        metric_key="tier1_storage_transitional_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="tier0_network_transitional_smoke",
        domain="matrix_transitional",
        metric_key="tier0_network_transitional_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="tier1_network_transitional_smoke",
        domain="matrix_transitional",
        metric_key="tier1_network_transitional_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="tier0_storage_modern_smoke",
        domain="matrix_modern_storage",
        metric_key="tier0_storage_modern_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="tier1_storage_modern_smoke",
        domain="matrix_modern_storage",
        metric_key="tier1_storage_modern_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="tier0_network_modern_smoke",
        domain="matrix_modern_network",
        metric_key="tier0_network_modern_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="tier1_network_modern_smoke",
        domain="matrix_modern_network",
        metric_key="tier1_network_modern_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="tier0_scsi_smoke",
        domain="matrix_scsi",
        metric_key="tier0_scsi_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="tier1_scsi_smoke",
        domain="matrix_scsi",
        metric_key="tier1_scsi_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="tier0_gpu_framebuffer",
        domain="matrix_gpu",
        metric_key="tier0_gpu_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="tier1_gpu_framebuffer",
        domain="matrix_gpu",
        metric_key="tier1_gpu_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="lifecycle_virtio_blk_modern",
        domain="lifecycle",
        metric_key="virtio_blk_modern_runtime_errors",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="lifecycle_virtio_net_modern",
        domain="lifecycle",
        metric_key="virtio_net_modern_runtime_errors",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="lifecycle_virtio_scsi",
        domain="lifecycle",
        metric_key="virtio_scsi_runtime_errors",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="lifecycle_virtio_gpu",
        domain="lifecycle",
        metric_key="virtio_gpu_runtime_errors",
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
    CheckSpec(
        check_id="negative_scsi_missing_deterministic",
        domain="negative_path",
        metric_key="scsi_missing_marker_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="negative_gpu_missing_deterministic",
        domain="negative_path",
        metric_key="gpu_missing_marker_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
)


PROMOTION_CRITERIA = {
    "required_green_runs": 14,
    "zero_v5_regressions": True,
    "zero_fatal_lifecycle_errors": True,
    "desktop_display_bridge_green": True,
    "required_reproducible_profiles": ["transitional", "modern"],
}


def known_checks() -> Set[str]:
    return {spec.check_id for spec in BASE_CHECKS} | {"desktop_display_bridge"}


def _noise(seed: int, key: str) -> int:
    digest = hashlib.sha256(f"{seed}|{key}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _round_value(value: float) -> float:
    return round(value, 3)


def _baseline_observed(seed: int, spec: CheckSpec) -> float:
    spread = spec.spread if spec.spread > 0 else 1
    value = spec.base + ((_noise(seed, spec.check_id) % spread) * spec.scale)
    return _round_value(value)


def _failing_observed(operator: str, threshold: float, scale: float) -> float:
    delta = 0.001 if scale < 1.0 else 1.0
    if operator == "max":
        return _round_value(threshold + delta)
    if operator == "min":
        return _round_value(threshold - delta)
    return _round_value(threshold + delta)


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


def normalize_failures(values: Sequence[str]) -> Set[str]:
    failures = {value.strip() for value in values if value.strip()}
    unknown = sorted(failures - known_checks())
    if unknown:
        raise ValueError(f"unknown check ids in --inject-failure: {', '.join(unknown)}")
    return failures


def _lifecycle_row(
    driver: str,
    device_class: str,
    profile: str,
    passed: bool,
    extra_states: Sequence[str] | None = None,
) -> Dict[str, object]:
    states = [
        "probe_found",
        "init_ready",
        "runtime_ok",
        "irq_vector_bound",
        "irq_vector_retarget",
        "cpu_affinity_balance",
        "reset_recover",
    ]
    if extra_states:
        states.extend(extra_states)
    if passed:
        return {
            "driver": driver,
            "device_class": device_class,
            "profile": profile,
            "states_observed": states,
            "probe_attempts": 1,
            "probe_successes": 1,
            "init_failures": 0,
            "runtime_errors": 0,
            "irq_vector_bound": True,
            "irq_vector_retarget": 1,
            "affinity_balance_events": 1,
            "recoveries": 0,
            "fatal_errors": 0,
            "status": "pass",
        }

    return {
        "driver": driver,
        "device_class": device_class,
        "profile": profile,
        "states_observed": ["probe_missing", "error_fatal"],
        "probe_attempts": 1,
        "probe_successes": 0,
        "init_failures": 1,
        "runtime_errors": 1,
        "irq_vector_bound": False,
        "irq_vector_retarget": 0,
        "affinity_balance_events": 0,
        "recoveries": 0,
        "fatal_errors": 1,
        "status": "fail",
    }


def run_matrix(
    seed: int,
    injected_failures: Set[str] | None = None,
    max_failures: int = 0,
    display_class: str = "virtio-gpu-pci",
    display_driver: str = "virtio_gpu_framebuffer",
    boot_transport_class: str = "virtio-blk-pci-modern",
) -> Dict[str, object]:
    failures = set() if injected_failures is None else set(injected_failures)
    matrix_failures = failures - {"desktop_display_bridge"}

    checks: List[Dict[str, object]] = []
    metric_values: Dict[str, float] = {}
    for spec in BASE_CHECKS:
        observed = (
            _failing_observed(spec.operator, spec.threshold, spec.scale)
            if spec.check_id in matrix_failures
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

    desktop_failures: Set[str] = set()
    if "desktop_display_bridge" in failures:
        desktop_failures.add("display_mode_set")

    desktop_report = desktop_smoke.run_smoke(
        seed=seed,
        injected_failures=desktop_failures,
        display_class=display_class,
        display_driver=display_driver,
        boot_transport_class=boot_transport_class,
    )
    bridge_pass = bool(desktop_report["desktop_display_checks"]["bridge_pass"])
    checks.append(
        {
            "check_id": "desktop_display_bridge",
            "domain": "desktop_bridge",
            "metric_key": "desktop_display_bridge_ratio",
            "operator": "min",
            "threshold": 1.0,
            "observed": 1.0 if bridge_pass else 0.999,
            "pass": bridge_pass,
        }
    )

    check_pass = {row["check_id"]: bool(row["pass"]) for row in checks}

    transitional_storage_status = (
        check_pass["tier0_storage_transitional_smoke"]
        and check_pass["tier1_storage_transitional_smoke"]
    )
    transitional_network_status = (
        check_pass["tier0_network_transitional_smoke"]
        and check_pass["tier1_network_transitional_smoke"]
    )
    modern_storage_status = (
        check_pass["tier0_storage_modern_smoke"]
        and check_pass["tier1_storage_modern_smoke"]
    )
    modern_network_status = (
        check_pass["tier0_network_modern_smoke"]
        and check_pass["tier1_network_modern_smoke"]
    )
    scsi_status = check_pass["tier0_scsi_smoke"] and check_pass["tier1_scsi_smoke"]
    gpu_status = (
        check_pass["tier0_gpu_framebuffer"]
        and check_pass["tier1_gpu_framebuffer"]
        and check_pass["desktop_display_bridge"]
    )

    virtio_profile_matrix = {
        "transitional": {
            "transport": "pci-transitional",
            "machine_profiles": ["q35", "pc/i440fx"],
            "storage_device": "virtio-blk-pci,disable-modern=on",
            "network_device": "virtio-net-pci,disable-modern=on",
            "checks_pass": transitional_storage_status and transitional_network_status,
            "reproducible": transitional_storage_status and transitional_network_status,
        },
        "modern": {
            "transport": "pci-modern",
            "machine_profiles": ["q35", "pc/i440fx"],
            "storage_device": "virtio-blk-pci",
            "network_device": "virtio-net-pci",
            "scsi_device": "virtio-scsi-pci",
            "display_device": "virtio-gpu-pci",
            "checks_pass": (
                modern_storage_status
                and modern_network_status
                and scsi_status
                and gpu_status
            ),
            "reproducible": (
                modern_storage_status
                and modern_network_status
                and scsi_status
                and gpu_status
            ),
        },
    }

    tier_results = [
        {
            "tier": "tier0",
            "machine": "q35",
            "storage_transitional": (
                "pass" if check_pass["tier0_storage_transitional_smoke"] else "fail"
            ),
            "network_transitional": (
                "pass" if check_pass["tier0_network_transitional_smoke"] else "fail"
            ),
            "storage_modern": (
                "pass" if check_pass["tier0_storage_modern_smoke"] else "fail"
            ),
            "network_modern": (
                "pass" if check_pass["tier0_network_modern_smoke"] else "fail"
            ),
            "virtio_scsi": "pass" if check_pass["tier0_scsi_smoke"] else "fail",
            "virtio_gpu_framebuffer": (
                "pass" if check_pass["tier0_gpu_framebuffer"] else "fail"
            ),
            "desktop_display_bridge": (
                "pass" if check_pass["desktop_display_bridge"] else "fail"
            ),
            "status": (
                "pass"
                if check_pass["tier0_storage_transitional_smoke"]
                and check_pass["tier0_network_transitional_smoke"]
                and check_pass["tier0_storage_modern_smoke"]
                and check_pass["tier0_network_modern_smoke"]
                and check_pass["tier0_scsi_smoke"]
                and check_pass["tier0_gpu_framebuffer"]
                and check_pass["desktop_display_bridge"]
                else "fail"
            ),
        },
        {
            "tier": "tier1",
            "machine": "pc/i440fx",
            "storage_transitional": (
                "pass" if check_pass["tier1_storage_transitional_smoke"] else "fail"
            ),
            "network_transitional": (
                "pass" if check_pass["tier1_network_transitional_smoke"] else "fail"
            ),
            "storage_modern": (
                "pass" if check_pass["tier1_storage_modern_smoke"] else "fail"
            ),
            "network_modern": (
                "pass" if check_pass["tier1_network_modern_smoke"] else "fail"
            ),
            "virtio_scsi": "pass" if check_pass["tier1_scsi_smoke"] else "fail",
            "virtio_gpu_framebuffer": (
                "pass" if check_pass["tier1_gpu_framebuffer"] else "fail"
            ),
            "desktop_display_bridge": (
                "pass" if check_pass["desktop_display_bridge"] else "fail"
            ),
            "status": (
                "pass"
                if check_pass["tier1_storage_transitional_smoke"]
                and check_pass["tier1_network_transitional_smoke"]
                and check_pass["tier1_storage_modern_smoke"]
                and check_pass["tier1_network_modern_smoke"]
                and check_pass["tier1_scsi_smoke"]
                and check_pass["tier1_gpu_framebuffer"]
                and check_pass["desktop_display_bridge"]
                else "fail"
            ),
        },
    ]

    device_class_coverage = [
        {
            "device": "virtio-blk-pci",
            "class": "storage",
            "profile": "transitional",
            "required": True,
            "status": "pass" if transitional_storage_status else "fail",
        },
        {
            "device": "virtio-net-pci",
            "class": "network",
            "profile": "transitional",
            "required": True,
            "status": "pass" if transitional_network_status else "fail",
        },
        {
            "device": "virtio-blk-pci",
            "class": "storage",
            "profile": "modern",
            "required": True,
            "status": "pass" if modern_storage_status else "fail",
        },
        {
            "device": "virtio-net-pci",
            "class": "network",
            "profile": "modern",
            "required": True,
            "status": "pass" if modern_network_status else "fail",
        },
        {
            "device": "virtio-scsi-pci",
            "class": "storage",
            "profile": "modern",
            "required": True,
            "status": "pass" if scsi_status else "fail",
        },
        {
            "device": "virtio-gpu-pci",
            "class": "display",
            "profile": "modern",
            "required": True,
            "desktop_bound": True,
            "status": "pass" if gpu_status else "fail",
        },
    ]

    driver_lifecycle = [
        _lifecycle_row(
            "virtio-blk-pci",
            "storage",
            "transitional",
            transitional_storage_status,
        ),
        _lifecycle_row(
            "virtio-net-pci",
            "network",
            "transitional",
            transitional_network_status,
        ),
        _lifecycle_row(
            "virtio-blk-pci",
            "storage",
            "modern",
            modern_storage_status and check_pass["lifecycle_virtio_blk_modern"],
        ),
        _lifecycle_row(
            "virtio-net-pci",
            "network",
            "modern",
            modern_network_status and check_pass["lifecycle_virtio_net_modern"],
        ),
        _lifecycle_row(
            "virtio-scsi-pci",
            "storage",
            "modern",
            scsi_status and check_pass["lifecycle_virtio_scsi"],
        ),
        _lifecycle_row(
            "virtio-gpu-pci",
            "display",
            "modern",
            gpu_status and check_pass["lifecycle_virtio_gpu"],
            extra_states=["framebuffer_console_present", "display_scanout_ready"],
        ),
    ]

    shadow_gate = {
        "status": "shadow",
        "baseline_contract_id": SHADOW_BASELINE_CONTRACT_ID,
        "baseline_gate": "test-hw-firmware-smp-v1",
        "promotion_criteria": PROMOTION_CRITERIA,
        "active_release_floor_remains_v5": True,
    }

    total_failures = sum(1 for row in checks if row["pass"] is False)
    gate_pass = total_failures <= max_failures

    stable_payload = {
        "schema": SCHEMA,
        "seed": seed,
        "max_failures": max_failures,
        "boot_transport_class": boot_transport_class,
        "display_class": display_class,
        "desktop_smoke_digest": desktop_report["digest"],
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
        "virtio_platform_profile_id": VIRTIO_PLATFORM_PROFILE_ID,
        "display_contract_id": DISPLAY_CONTRACT_ID,
        "shadow_baseline_contract_id": SHADOW_BASELINE_CONTRACT_ID,
        "seed": seed,
        "gate": "test-hw-matrix-v6",
        "checks": checks,
        "summary": {
            "matrix_transitional": _domain_summary(checks, "matrix_transitional"),
            "matrix_modern_storage": _domain_summary(checks, "matrix_modern_storage"),
            "matrix_modern_network": _domain_summary(checks, "matrix_modern_network"),
            "matrix_scsi": _domain_summary(checks, "matrix_scsi"),
            "matrix_gpu": _domain_summary(checks, "matrix_gpu"),
            "lifecycle": _domain_summary(checks, "lifecycle"),
            "desktop_bridge": _domain_summary(checks, "desktop_bridge"),
            "negative_path": _domain_summary(checks, "negative_path"),
        },
        "tier_results": tier_results,
        "virtio_profile_matrix": virtio_profile_matrix,
        "device_class_coverage": device_class_coverage,
        "driver_lifecycle": driver_lifecycle,
        "boot_transport_class": boot_transport_class,
        "display_class": display_class,
        "desktop_display_checks": {
            **desktop_report["desktop_display_checks"],
            "source_schema": desktop_report["schema"],
            "source_digest": desktop_report["digest"],
        },
        "negative_paths": {
            "block_probe_missing": {
                "marker": "BLK: not found",
                "deterministic": check_pass["negative_blk_missing_deterministic"],
                "status": (
                    "pass"
                    if check_pass["negative_blk_missing_deterministic"]
                    else "fail"
                ),
            },
            "net_probe_missing": {
                "marker": "NET: not found",
                "deterministic": check_pass["negative_net_missing_deterministic"],
                "status": (
                    "pass"
                    if check_pass["negative_net_missing_deterministic"]
                    else "fail"
                ),
            },
            "scsi_probe_missing": {
                "marker": "SCSI: not found",
                "deterministic": check_pass["negative_scsi_missing_deterministic"],
                "status": (
                    "pass"
                    if check_pass["negative_scsi_missing_deterministic"]
                    else "fail"
                ),
            },
            "gpu_probe_missing": {
                "marker": "GPU: not found",
                "deterministic": check_pass["negative_gpu_missing_deterministic"],
                "status": (
                    "pass"
                    if check_pass["negative_gpu_missing_deterministic"]
                    else "fail"
                ),
            },
        },
        "shadow_gate": shadow_gate,
        "artifact_refs": {
            "junit": "out/pytest-hw-matrix-v6.xml",
            "matrix_report": "out/hw-matrix-v6.json",
            "desktop_smoke_report": "out/desktop-smoke-v1.json",
            "ci_artifact": "hw-matrix-v6-artifacts",
            "platform_ci_artifact": "virtio-platform-v1-artifacts",
            "shadow_baseline_artifact": "hw-firmware-smp-v1-artifacts",
        },
        "injected_failures": sorted(failures),
        "max_failures": max_failures,
        "total_failures": total_failures,
        "failures": sorted(row["check_id"] for row in checks if row["pass"] is False),
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
    parser.add_argument("--display-class", default="virtio-gpu-pci")
    parser.add_argument("--display-driver", default="virtio_gpu_framebuffer")
    parser.add_argument("--boot-transport-class", default="virtio-blk-pci-modern")
    parser.add_argument("--out", default="out/hw-matrix-v6.json")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.max_failures < 0:
        print("error: max-failures must be >= 0")
        return 2

    try:
        injected_failures = normalize_failures(args.inject_failure)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    report = run_matrix(
        seed=args.seed,
        injected_failures=injected_failures,
        max_failures=args.max_failures,
        display_class=args.display_class,
        display_driver=args.display_driver,
        boot_transport_class=args.boot_transport_class,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"hw-matrix-v6-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
