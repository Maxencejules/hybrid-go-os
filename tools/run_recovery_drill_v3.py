#!/usr/bin/env python3
"""Run deterministic recovery workflow drill artifacts for M30."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set

import release_bundle_v1 as release_bundle


SCHEMA = "rugo.recovery_drill.v3"
CONTRACT_ID = "rugo.installer_ux_contract.v3"
WORKFLOW_ID = "rugo.recovery_workflow.v3"
STAGES = [
    "recovery_entry_validation",
    "rollback_snapshot_mount",
    "state_reconciliation",
    "service_restore_validation",
    "post_recovery_audit",
]


def _metric(seed: int, stage: str, label: str, base: int, spread: int) -> int:
    digest = hashlib.sha256(f"{seed}|{stage}|{label}".encode("utf-8")).hexdigest()
    return base + (int(digest[:8], 16) % spread)


def _collect_injected(values: List[str]) -> Set[str]:
    requested = {value.strip() for value in values if value.strip()}
    unknown = sorted(requested - set(STAGES))
    if unknown:
        raise ValueError(f"unknown stages in --inject-failure: {', '.join(unknown)}")
    return requested


def run_recovery_drill(
    seed: int,
    bundle: Dict[str, object] | None = None,
    install_state: Dict[str, object] | None = None,
    forced_failures: Set[str] | None = None,
    operator_checklist_completed: bool = True,
) -> Dict[str, object]:
    failures = set() if forced_failures is None else set(forced_failures)
    stages: List[Dict[str, object]] = []

    state_capture_complete = False
    triage_bundle_required = True
    runtime_capture = dict((bundle or {}).get("runtime_capture", {}))
    bundle_digest = str((bundle or {}).get("digest", ""))
    active_slot = str((install_state or {}).get("active_slot", "A"))
    recovery_media = ""
    recovery_sha256 = ""
    if bundle is not None:
        recovery_artifact = release_bundle.artifact_by_role(bundle, "recovery_image")
        recovery_media = str(recovery_artifact["path"])
        recovery_sha256 = str(recovery_artifact["sha256"])

    for stage in STAGES:
        auto_fail = stage == "post_recovery_audit" and not operator_checklist_completed
        failed = stage in failures or auto_fail
        status = "fail" if failed else "pass"

        details = (
            "simulated failure injected for validation"
            if stage in failures
            else (
                "operator checklist missing"
                if auto_fail
                else "stage completed within contract budget"
            )
        )

        entry: Dict[str, object] = {
            "name": stage,
            "status": status,
            "duration_ms": _metric(seed, stage, "duration_ms", base=700, spread=3900),
            "details": details,
            "active_slot_before": active_slot,
        }
        if recovery_media and stage in {
            "recovery_entry_validation",
            "rollback_snapshot_mount",
        }:
            entry["recovery_media_path"] = recovery_media
            entry["recovery_media_sha256"] = recovery_sha256
        if stage == "service_restore_validation":
            entry["runtime_capture_id"] = runtime_capture.get("capture_id", "")
            entry["trace_id"] = runtime_capture.get("trace_id", "")

        if stage == "post_recovery_audit":
            state_capture_complete = status == "pass"
            entry["checks"] = {
                "operator_checklist_completed": operator_checklist_completed,
                "triage_bundle_required": triage_bundle_required,
                "state_capture_complete": state_capture_complete,
                "release_bundle_digest_present": bool(bundle_digest),
            }

        stages.append(entry)

    failed_cases = sum(1 for stage in stages if stage["status"] != "pass")
    passed_cases = len(stages) - failed_cases

    return {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "workflow_id": WORKFLOW_ID,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed": seed,
        "release_bundle_digest": bundle_digest,
        "runtime_capture_id": runtime_capture.get("capture_id", ""),
        "total_cases": len(stages),
        "passed_cases": passed_cases,
        "failed_cases": failed_cases,
        "total_failures": failed_cases,
        "stages": stages,
        "state_transition": {
            "active_slot_before": active_slot,
            "active_slot_after": active_slot,
        },
        "recovery_readiness": {
            "operator_checklist_completed": operator_checklist_completed,
            "triage_bundle_required": triage_bundle_required,
            "state_capture_complete": state_capture_complete,
        },
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20260309)
    parser.add_argument("--max-failures", type=int, default=0)
    parser.add_argument("--release-bundle", default="")
    parser.add_argument("--install-state", default="")
    parser.add_argument(
        "--inject-failure",
        action="append",
        default=[],
        help="force a named stage into failure state",
    )
    parser.add_argument(
        "--skip-operator-checklist",
        action="store_true",
        help="simulate missing operator checklist completion",
    )
    parser.add_argument("--out", default="out/recovery-drill-v3.json")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    bundle = (
        release_bundle.load_bundle(Path(args.release_bundle))
        if args.release_bundle
        else None
    )
    install_state = (
        release_bundle.load_install_state(Path(args.install_state))
        if args.install_state
        else None
    )

    try:
        injected_failures = _collect_injected(args.inject_failure)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    report = run_recovery_drill(
        seed=args.seed,
        bundle=bundle,
        install_state=install_state,
        forced_failures=injected_failures,
        operator_checklist_completed=not args.skip_operator_checklist,
    )
    report["max_failures"] = args.max_failures
    readiness = report["recovery_readiness"]
    report["meets_target"] = (
        report["total_failures"] <= args.max_failures
        and readiness["operator_checklist_completed"] is True
        and readiness["state_capture_complete"] is True
    )
    report["gate_pass"] = report["meets_target"]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"recovery-drill-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    print(f"operator_checklist_completed: {readiness['operator_checklist_completed']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
