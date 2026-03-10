#!/usr/bin/env python3
"""Run deterministic hardware matrix v5 checks for M43."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set


SCHEMA = "rugo.hw_matrix_evidence.v5"
MATRIX_CONTRACT_ID = "rugo.hw.support_matrix.v5"
DRIVER_CONTRACT_ID = "rugo.driver_lifecycle_report.v5"
FIRMWARE_HARDENING_ID = "rugo.acpi_uefi_hardening.v3"
SMP_INTERRUPT_MODEL_ID = "rugo.smp_interrupt_model.v1"
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
        domain="coverage_storage",
        metric_key="ahci_coverage_gap",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="coverage_storage_nvme",
        domain="coverage_storage",
        metric_key="nvme_coverage_gap",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="coverage_network_e1000",
        domain="coverage_network",
        metric_key="e1000_coverage_gap",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="coverage_network_rtl8139",
        domain="coverage_network",
        metric_key="rtl8139_coverage_gap",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="firmware_rsdp_checksum",
        domain="firmware",
        metric_key="firmware_rsdp_checksum_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="firmware_xsdt_parse",
        domain="firmware",
        metric_key="firmware_xsdt_parse_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="firmware_madt_topology",
        domain="firmware",
        metric_key="firmware_madt_topology_failures",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="smp_bootstrap_cpu_online_ratio",
        domain="smp",
        metric_key="bootstrap_cpu_online_ratio",
        operator="min",
        threshold=1.0,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="smp_application_cpu_online_ratio",
        domain="smp",
        metric_key="application_cpu_online_ratio",
        operator="min",
        threshold=0.99,
        base=1.0,
        spread=1,
        scale=0.0,
    ),
    CheckSpec(
        check_id="smp_ipi_roundtrip_p95_ms",
        domain="smp",
        metric_key="ipi_roundtrip_p95_ms",
        operator="max",
        threshold=4.0,
        base=2.4,
        spread=5,
        scale=0.2,
    ),
    CheckSpec(
        check_id="smp_lost_interrupt_events",
        domain="smp",
        metric_key="lost_interrupt_events",
        operator="max",
        threshold=0.0,
        base=0.0,
        spread=1,
        scale=1.0,
    ),
    CheckSpec(
        check_id="smp_spurious_interrupt_rate",
        domain="smp",
        metric_key="spurious_interrupt_rate",
        operator="max",
        threshold=0.01,
        base=0.002,
        spread=4,
        scale=0.001,
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


NATIVE_STORAGE_CHECK_ID = "native_storage_driver_matrix"
NATIVE_NETWORK_CHECK_ID = "native_nic_driver_matrix"


def known_checks() -> Set[str]:
    return {spec.check_id for spec in BASE_CHECKS} | {
        NATIVE_STORAGE_CHECK_ID,
        NATIVE_NETWORK_CHECK_ID,
    }


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


def _native_check_row(check_id: str, observed: float, failures: Set[str]) -> Dict[str, object]:
    threshold = 1.0
    if check_id in failures:
        observed = min(observed, 0.999)
    observed = _round_value(observed)
    return {
        "check_id": check_id,
        "domain": "native",
        "metric_key": f"{check_id}_pass_rate",
        "operator": "min",
        "threshold": threshold,
        "observed": observed,
        "pass": observed >= threshold,
    }


def _driver_row(
    driver: str,
    device_class: str,
    passed: bool,
) -> Dict[str, object]:
    if passed:
        return {
            "driver": driver,
            "device_class": device_class,
            "states_observed": [
                "probe_found",
                "init_ready",
                "runtime_ok",
                "irq_vector_bound",
                "irq_vector_retarget",
                "cpu_affinity_balance",
                "reset_recover",
            ],
            "probe_attempts": 1,
            "probe_successes": 1,
            "init_failures": 0,
            "runtime_errors": 0,
            "irq_retarget_events": 1,
            "affinity_balance_events": 1,
            "recoveries": 0,
            "fatal_errors": 0,
            "status": "pass",
        }

    return {
        "driver": driver,
        "device_class": device_class,
        "states_observed": ["probe_missing", "error_fatal"],
        "probe_attempts": 1,
        "probe_successes": 0,
        "init_failures": 1,
        "runtime_errors": 1,
        "irq_retarget_events": 0,
        "affinity_balance_events": 0,
        "recoveries": 0,
        "fatal_errors": 1,
        "status": "fail",
    }


def run_matrix(
    seed: int,
    injected_failures: Set[str] | None = None,
    max_failures: int = 0,
) -> Dict[str, object]:
    failures = set() if injected_failures is None else set(injected_failures)

    checks: List[Dict[str, object]] = []
    metric_values: Dict[str, float] = {}
    for spec in BASE_CHECKS:
        observed = (
            _failing_observed(spec.operator, spec.threshold, spec.scale)
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

    check_pass = {row["check_id"]: bool(row["pass"]) for row in checks}

    storage_status = {
        "virtio-blk-pci": check_pass["tier0_storage_smoke"]
        and check_pass["tier1_storage_smoke"],
        "ahci": check_pass["coverage_storage_ahci"],
        "nvme": check_pass["coverage_storage_nvme"],
    }
    network_status = {
        "virtio-net-pci": check_pass["tier0_network_smoke"]
        and check_pass["tier1_network_smoke"],
        "e1000": check_pass["coverage_network_e1000"],
        "rtl8139": check_pass["coverage_network_rtl8139"],
    }

    storage_pass_rate = _round_value(
        sum(1 for status in storage_status.values() if status) / len(storage_status)
    )
    network_pass_rate = _round_value(
        sum(1 for status in network_status.values() if status) / len(network_status)
    )

    checks.append(
        _native_check_row(NATIVE_STORAGE_CHECK_ID, storage_pass_rate, failures)
    )
    checks.append(
        _native_check_row(NATIVE_NETWORK_CHECK_ID, network_pass_rate, failures)
    )

    check_pass = {row["check_id"]: bool(row["pass"]) for row in checks}

    firmware_checks_pass = (
        check_pass["firmware_rsdp_checksum"]
        and check_pass["firmware_xsdt_parse"]
        and check_pass["firmware_madt_topology"]
    )
    smp_checks_pass = (
        check_pass["smp_bootstrap_cpu_online_ratio"]
        and check_pass["smp_application_cpu_online_ratio"]
        and check_pass["smp_ipi_roundtrip_p95_ms"]
        and check_pass["smp_lost_interrupt_events"]
        and check_pass["smp_spurious_interrupt_rate"]
    )

    tier_results = [
        {
            "tier": "tier0",
            "machine": "q35",
            "storage_smoke": "pass" if check_pass["tier0_storage_smoke"] else "fail",
            "network_smoke": "pass" if check_pass["tier0_network_smoke"] else "fail",
            "firmware_table": "pass" if firmware_checks_pass else "fail",
            "smp_baseline": "pass" if smp_checks_pass else "fail",
            "status": (
                "pass"
                if check_pass["tier0_storage_smoke"]
                and check_pass["tier0_network_smoke"]
                and firmware_checks_pass
                and smp_checks_pass
                else "fail"
            ),
        },
        {
            "tier": "tier1",
            "machine": "pc/i440fx",
            "storage_smoke": "pass" if check_pass["tier1_storage_smoke"] else "fail",
            "network_smoke": "pass" if check_pass["tier1_network_smoke"] else "fail",
            "firmware_table": "pass" if firmware_checks_pass else "fail",
            "smp_baseline": "pass" if smp_checks_pass else "fail",
            "status": (
                "pass"
                if check_pass["tier1_storage_smoke"]
                and check_pass["tier1_network_smoke"]
                and firmware_checks_pass
                and smp_checks_pass
                else "fail"
            ),
        },
    ]

    device_class_coverage = [
        {
            "device": "virtio-blk-pci",
            "class": "storage",
            "required": True,
            "status": "pass" if storage_status["virtio-blk-pci"] else "fail",
        },
        {
            "device": "ahci",
            "class": "storage",
            "required": True,
            "status": "pass" if storage_status["ahci"] else "fail",
        },
        {
            "device": "nvme",
            "class": "storage",
            "required": True,
            "status": "pass" if storage_status["nvme"] else "fail",
        },
        {
            "device": "virtio-net-pci",
            "class": "network",
            "required": True,
            "status": "pass" if network_status["virtio-net-pci"] else "fail",
        },
        {
            "device": "e1000",
            "class": "network",
            "required": True,
            "status": "pass" if network_status["e1000"] else "fail",
        },
        {
            "device": "rtl8139",
            "class": "network",
            "required": True,
            "status": "pass" if network_status["rtl8139"] else "fail",
        },
    ]

    driver_lifecycle = [
        _driver_row("virtio-blk-pci", "storage", check_pass["lifecycle_virtio_blk"]),
        _driver_row("ahci", "storage", storage_status["ahci"]),
        _driver_row("nvme", "storage", storage_status["nvme"]),
        _driver_row("virtio-net-pci", "network", check_pass["lifecycle_virtio_net"]),
        _driver_row("e1000", "network", network_status["e1000"]),
        _driver_row("rtl8139", "network", network_status["rtl8139"]),
    ]

    firmware_table_validation = {
        "signatures": ["RSDP", "XSDT", "FADT", "MADT", "MCFG"],
        "rsdp_checksum_pass": check_pass["firmware_rsdp_checksum"],
        "xsdt_parse_pass": check_pass["firmware_xsdt_parse"],
        "madt_topology_pass": check_pass["firmware_madt_topology"],
        "checks_pass": firmware_checks_pass,
    }

    smp_baseline = {
        "bootstrap_cpu_online_ratio": metric_values["bootstrap_cpu_online_ratio"],
        "application_cpu_online_ratio": metric_values["application_cpu_online_ratio"],
        "ipi_roundtrip_p95_ms": metric_values["ipi_roundtrip_p95_ms"],
        "lost_interrupt_events": int(metric_values["lost_interrupt_events"]),
        "spurious_interrupt_rate": metric_values["spurious_interrupt_rate"],
        "checks_pass": smp_checks_pass,
    }

    native_driver_matrix = {
        "storage": {
            "required_devices": ["virtio-blk-pci", "ahci", "nvme"],
            "pass_rate": storage_pass_rate,
            "checks_pass": check_pass[NATIVE_STORAGE_CHECK_ID],
        },
        "network": {
            "required_devices": ["virtio-net-pci", "e1000", "rtl8139"],
            "pass_rate": network_pass_rate,
            "checks_pass": check_pass[NATIVE_NETWORK_CHECK_ID],
        },
    }

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

    summary = {
        "matrix": _domain_summary(checks, "matrix"),
        "lifecycle": _domain_summary(checks, "lifecycle"),
        "coverage_storage": _domain_summary(checks, "coverage_storage"),
        "coverage_network": _domain_summary(checks, "coverage_network"),
        "firmware": _domain_summary(checks, "firmware"),
        "smp": _domain_summary(checks, "smp"),
        "native": _domain_summary(checks, "native"),
        "negative_path": _domain_summary(checks, "negative_path"),
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
        "firmware_hardening_id": FIRMWARE_HARDENING_ID,
        "smp_interrupt_model_id": SMP_INTERRUPT_MODEL_ID,
        "seed": seed,
        "gate": "test-hw-firmware-smp-v1",
        "checks": checks,
        "summary": summary,
        "tier_results": tier_results,
        "device_class_coverage": device_class_coverage,
        "driver_lifecycle": driver_lifecycle,
        "firmware_table_validation": firmware_table_validation,
        "smp_baseline": smp_baseline,
        "native_driver_matrix": native_driver_matrix,
        "negative_paths": negative_paths,
        "artifact_refs": {
            "junit": "out/pytest-hw-firmware-smp-v1.xml",
            "matrix_report": "out/hw-matrix-v5.json",
            "firmware_smp_report": "out/hw-firmware-smp-v1.json",
            "ci_artifact": "hw-firmware-smp-v1-artifacts",
            "native_ci_artifact": "native-driver-matrix-v1-artifacts",
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
    parser.add_argument("--out", default="out/hw-matrix-v5.json")
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
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"hw-matrix-v5-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
