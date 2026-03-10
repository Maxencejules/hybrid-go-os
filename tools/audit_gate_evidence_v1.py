#!/usr/bin/env python3
"""Audit runtime evidence provenance and enforce synthetic-evidence ban for M40."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set

import collect_runtime_evidence_v1 as collector


SCHEMA = "rugo.gate_evidence_audit_report.v1"
AUDIT_POLICY_ID = "rugo.gate_provenance_policy.v1"
EVIDENCE_POLICY_ID = "rugo.evidence_integrity_policy.v1"
RUNTIME_SCHEMA_ID = "rugo.runtime_evidence_schema.v1"


def _known_checks() -> Set[str]:
    return {spec.check_id for spec in collector.CHECKS}


def _normalize_failures(values: Sequence[str]) -> Set[str]:
    failures = {value.strip() for value in values if value.strip()}
    unknown = sorted(failures - _known_checks())
    if unknown:
        raise ValueError(f"unknown check ids in --inject-failure: {', '.join(unknown)}")
    return failures


def _read_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _append_check(
    checks: List[Dict[str, object]],
    *,
    check_id: str,
    domain: str,
    passed: bool,
    detail: str = "",
) -> None:
    checks.append(
        {
            "check_id": check_id,
            "domain": domain,
            "pass": bool(passed),
            "detail": detail,
        }
    )


def _domain_summary(checks: List[Dict[str, object]], domain: str) -> Dict[str, object]:
    scoped = [entry for entry in checks if entry["domain"] == domain]
    failures = [entry for entry in scoped if entry["pass"] is False]
    return {
        "checks": len(scoped),
        "failures": len(failures),
        "pass": len(failures) == 0,
    }


def run_audit(
    *,
    evidence: Dict[str, object],
    evidence_present: bool,
    input_evidence_path: str,
) -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    _append_check(
        checks,
        check_id="evidence_file_present",
        domain="identity",
        passed=evidence_present,
        detail=input_evidence_path or "generated-in-memory",
    )

    schema_valid = evidence.get("schema") == collector.SCHEMA
    _append_check(
        checks,
        check_id="evidence_schema_valid",
        domain="identity",
        passed=schema_valid,
    )

    _append_check(
        checks,
        check_id="evidence_policy_id_match",
        domain="identity",
        passed=evidence.get("evidence_integrity_policy_id") == EVIDENCE_POLICY_ID,
    )
    _append_check(
        checks,
        check_id="runtime_schema_id_match",
        domain="identity",
        passed=evidence.get("runtime_evidence_schema_id") == RUNTIME_SCHEMA_ID,
    )
    _append_check(
        checks,
        check_id="gate_provenance_policy_match",
        domain="identity",
        passed=evidence.get("gate_provenance_policy_id") == AUDIT_POLICY_ID,
    )

    evidence_checks = {}
    for row in evidence.get("checks", []):
        if isinstance(row, dict) and row.get("check_id"):
            evidence_checks[str(row["check_id"])] = row

    for check_id in [
        "runtime_capture_ratio",
        "trace_linkage_ratio",
        "provenance_fields_ratio",
        "synthetic_evidence_ratio",
        "synthetic_only_artifacts",
        "detached_trace_count",
        "unsigned_artifact_count",
    ]:
        row = evidence_checks.get(check_id)
        passed = isinstance(row, dict) and row.get("pass") is True
        domain = "synthetic" if check_id.startswith("synthetic") or check_id.startswith("detached") else "provenance"
        _append_check(
            checks,
            check_id=check_id,
            domain=domain,
            passed=passed,
        )

    lanes = {
        item.get("execution_lane")
        for item in evidence.get("evidence_items", [])
        if isinstance(item, dict)
    }
    _append_check(
        checks,
        check_id="runtime_lane_coverage",
        domain="provenance",
        passed={"qemu", "baremetal"}.issubset(lanes),
    )

    _append_check(
        checks,
        check_id="release_gate_binding",
        domain="wiring",
        passed=evidence.get("gate") == "test-evidence-integrity-v1",
    )

    total_failures = sum(1 for check in checks if check["pass"] is False)
    summary = {
        "identity": _domain_summary(checks, "identity"),
        "provenance": _domain_summary(checks, "provenance"),
        "synthetic": _domain_summary(checks, "synthetic"),
        "wiring": _domain_summary(checks, "wiring"),
    }
    failures = sorted(check["check_id"] for check in checks if check["pass"] is False)

    stable_payload = {
        "schema": SCHEMA,
        "input_evidence_path": input_evidence_path,
        "input_digest": evidence.get("digest", ""),
        "checks": [
            {"check_id": check["check_id"], "pass": check["pass"]} for check in checks
        ],
    }
    digest = hashlib.sha256(
        json.dumps(stable_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return {
        "schema": SCHEMA,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "audit_policy_id": AUDIT_POLICY_ID,
        "evidence_integrity_policy_id": EVIDENCE_POLICY_ID,
        "runtime_evidence_schema_id": RUNTIME_SCHEMA_ID,
        "required_evidence_schema": collector.SCHEMA,
        "gate": "test-synthetic-evidence-ban-v1",
        "input_evidence_path": input_evidence_path,
        "input_evidence_digest": evidence.get("digest", ""),
        "evidence_gate_pass": evidence.get("gate_pass"),
        "checks": checks,
        "summary": summary,
        "total_failures": total_failures,
        "failures": failures,
        "artifact_refs": {
            "runtime_evidence_report": "out/runtime-evidence-v1.json",
            "gate_evidence_audit_report": "out/gate-evidence-audit-v1.json",
            "junit": "out/pytest-synthetic-evidence-ban-v1.xml",
            "ci_artifact": "synthetic-evidence-ban-v1-artifacts",
        },
        "digest": digest,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence",
        default="",
        help="path to runtime evidence report; if omitted, generate in-memory evidence",
    )
    parser.add_argument("--seed", type=int, default=collector.DEFAULT_SEED)
    parser.add_argument(
        "--inject-failure",
        action="append",
        default=[],
        help="force a collector check failure when generating in-memory evidence",
    )
    parser.add_argument("--max-failures", type=int, default=0)
    parser.add_argument("--out", default="out/gate-evidence-audit-v1.json")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.max_failures < 0:
        print("error: max-failures must be >= 0")
        return 2
    if args.evidence and args.inject_failure:
        print("error: --inject-failure cannot be used with --evidence")
        return 2

    evidence_present = False
    input_evidence_path = args.evidence
    evidence: Dict[str, object] = {}

    if args.evidence:
        evidence_path = Path(args.evidence)
        if evidence_path.is_file():
            evidence = _read_json(evidence_path)
            evidence_present = True
    else:
        try:
            injected_failures = _normalize_failures(args.inject_failure)
        except ValueError as exc:
            print(f"error: {exc}")
            return 2
        evidence = collector.collect_runtime_evidence(
            seed=args.seed,
            injected_failures=injected_failures,
        )
        evidence_present = True
        input_evidence_path = "<generated>"

    report = run_audit(
        evidence=evidence,
        evidence_present=evidence_present,
        input_evidence_path=input_evidence_path,
    )
    report["max_failures"] = args.max_failures
    report["gate_pass"] = report["total_failures"] <= args.max_failures

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"gate-evidence-audit-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
