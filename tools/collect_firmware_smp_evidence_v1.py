#!/usr/bin/env python3
"""Collect deterministic firmware + SMP evidence for M43."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set

import run_hw_matrix_v5 as matrix


SCHEMA = "rugo.hw_firmware_smp_evidence.v1"
FIRMWARE_HARDENING_ID = "rugo.acpi_uefi_hardening.v3"
SMP_INTERRUPT_MODEL_ID = "rugo.smp_interrupt_model.v1"
MATRIX_SCHEMA = "rugo.hw_matrix_evidence.v5"
DEFAULT_SEED = 20260310
REQUIRED_ARTIFACT_KEYS = (
    "junit",
    "matrix_report",
    "firmware_smp_report",
    "ci_artifact",
    "native_ci_artifact",
)


def _normalize_strings(values: Sequence[str]) -> Set[str]:
    return {value.strip() for value in values if value.strip()}


def _validate_missing_artifacts(missing: Set[str]) -> None:
    unknown = sorted(missing - set(REQUIRED_ARTIFACT_KEYS))
    if unknown:
        raise ValueError(
            "unknown artifacts in --inject-missing-artifact: " + ", ".join(unknown)
        )


def _policy_row_eq(check_id: str, observed: bool) -> Dict[str, object]:
    return {
        "check_id": check_id,
        "operator": "eq",
        "threshold": True,
        "observed": observed,
        "pass": observed is True,
    }


def _policy_row_max(check_id: str, observed: float, threshold: float) -> Dict[str, object]:
    return {
        "check_id": check_id,
        "operator": "max",
        "threshold": threshold,
        "observed": observed,
        "pass": observed <= threshold,
    }


def run_collection(
    seed: int,
    injected_failures: Set[str] | None = None,
    missing_artifacts: Set[str] | None = None,
) -> Dict[str, object]:
    failures = set() if injected_failures is None else set(injected_failures)
    missing = set() if missing_artifacts is None else set(missing_artifacts)

    matrix_report = matrix.run_matrix(
        seed=seed,
        injected_failures=failures,
        max_failures=0,
    )
    firmware = matrix_report["firmware_table_validation"]
    smp = matrix_report["smp_baseline"]
    native = matrix_report["native_driver_matrix"]

    native_checks_pass = bool(
        native["storage"]["checks_pass"] and native["network"]["checks_pass"]
    )

    policy_checks = [
        _policy_row_eq("matrix_gate_pass", bool(matrix_report["gate_pass"])),
        _policy_row_eq("firmware_checks_pass", bool(firmware["checks_pass"])),
        _policy_row_eq("smp_checks_pass", bool(smp["checks_pass"])),
        _policy_row_eq("native_driver_checks_pass", native_checks_pass),
        _policy_row_max(
            "no_lost_interrupts",
            float(smp["lost_interrupt_events"]),
            threshold=0.0,
        ),
        _policy_row_max(
            "ipi_roundtrip_budget",
            float(smp["ipi_roundtrip_p95_ms"]),
            threshold=4.0,
        ),
        _policy_row_eq("artifact_bundle_complete", len(missing) == 0),
    ]

    failures_list = sorted(
        check["check_id"] for check in policy_checks if check["pass"] is False
    )
    total_failures = len(failures_list)

    available_artifacts = sorted(
        key for key in REQUIRED_ARTIFACT_KEYS if key not in missing
    )

    stable_payload = {
        "schema": SCHEMA,
        "seed": seed,
        "source_matrix_digest": matrix_report["digest"],
        "injected_failures": sorted(failures),
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
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "firmware_hardening_id": FIRMWARE_HARDENING_ID,
        "smp_interrupt_model_id": SMP_INTERRUPT_MODEL_ID,
        "matrix_schema_id": MATRIX_SCHEMA,
        "seed": seed,
        "gate": "test-hw-firmware-smp-v1",
        "source_matrix_digest": matrix_report["digest"],
        "source_matrix_failures": matrix_report["failures"],
        "firmware_table_validation": firmware,
        "smp_baseline": smp,
        "native_driver_matrix": native,
        "summary": {
            "firmware": {"pass": bool(firmware["checks_pass"])},
            "smp": {"pass": bool(smp["checks_pass"])},
            "native": {"pass": native_checks_pass},
            "policy": {
                "checks": len(policy_checks),
                "failures": total_failures,
                "pass": total_failures == 0,
            },
        },
        "artifact_refs": matrix_report["artifact_refs"],
        "available_artifacts": available_artifacts,
        "missing_artifacts": sorted(missing),
        "policy_checks": policy_checks,
        "injected_failures": sorted(failures),
        "total_failures": total_failures,
        "failures": failures_list,
        "gate_pass": total_failures == 0,
        "digest": digest,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--inject-failure",
        action="append",
        default=[],
        help="force a matrix check to fail by check_id",
    )
    parser.add_argument(
        "--inject-missing-artifact",
        action="append",
        default=[],
        help="remove required artifact key from bundle",
    )
    parser.add_argument("--max-failures", type=int, default=0)
    parser.add_argument("--out", default="out/hw-firmware-smp-v1.json")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.max_failures < 0:
        print("error: max-failures must be >= 0")
        return 2

    try:
        injected_failures = matrix.normalize_failures(args.inject_failure)
        missing = _normalize_strings(args.inject_missing_artifact)
        _validate_missing_artifacts(missing)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    report = run_collection(
        seed=args.seed,
        injected_failures=injected_failures,
        missing_artifacts=missing,
    )
    report["max_failures"] = args.max_failures
    report["gate_pass"] = report["total_failures"] <= args.max_failures

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"hw-firmware-smp-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
