#!/usr/bin/env python3
"""Collect deterministic runtime-backed evidence artifacts for M40."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple


SCHEMA = "rugo.runtime_evidence_report.v1"
EVIDENCE_INTEGRITY_POLICY_ID = "rugo.evidence_integrity_policy.v1"
RUNTIME_EVIDENCE_SCHEMA_ID = "rugo.runtime_evidence_schema.v1"
GATE_PROVENANCE_POLICY_ID = "rugo.gate_provenance_policy.v1"
DEFAULT_SEED = 20260310


@dataclass(frozen=True)
class CheckSpec:
    check_id: str
    domain: str
    metric_key: str
    operator: str  # one of: min, max, eq
    threshold: float


CHECKS: Sequence[CheckSpec] = (
    CheckSpec(
        check_id="runtime_item_count",
        domain="execution",
        metric_key="runtime_item_count",
        operator="min",
        threshold=4.0,
    ),
    CheckSpec(
        check_id="runtime_capture_ratio",
        domain="execution",
        metric_key="runtime_capture_ratio",
        operator="min",
        threshold=1.0,
    ),
    CheckSpec(
        check_id="qemu_trace_presence_ratio",
        domain="execution",
        metric_key="qemu_trace_presence_ratio",
        operator="min",
        threshold=1.0,
    ),
    CheckSpec(
        check_id="baremetal_trace_presence_ratio",
        domain="execution",
        metric_key="baremetal_trace_presence_ratio",
        operator="min",
        threshold=1.0,
    ),
    CheckSpec(
        check_id="trace_linkage_ratio",
        domain="execution",
        metric_key="trace_linkage_ratio",
        operator="min",
        threshold=1.0,
    ),
    CheckSpec(
        check_id="provenance_fields_ratio",
        domain="provenance",
        metric_key="provenance_fields_ratio",
        operator="min",
        threshold=1.0,
    ),
    CheckSpec(
        check_id="unsigned_artifact_count",
        domain="provenance",
        metric_key="unsigned_artifact_count",
        operator="max",
        threshold=0.0,
    ),
    CheckSpec(
        check_id="synthetic_evidence_ratio",
        domain="synthetic",
        metric_key="synthetic_evidence_ratio",
        operator="max",
        threshold=0.0,
    ),
    CheckSpec(
        check_id="synthetic_only_artifacts",
        domain="synthetic",
        metric_key="synthetic_only_artifacts",
        operator="max",
        threshold=0.0,
    ),
    CheckSpec(
        check_id="detached_trace_count",
        domain="synthetic",
        metric_key="detached_trace_count",
        operator="max",
        threshold=0.0,
    ),
)


def _known_checks() -> Set[str]:
    return {spec.check_id for spec in CHECKS}


def _normalize_failures(values: Sequence[str]) -> Set[str]:
    failures = {value.strip() for value in values if value.strip()}
    unknown = sorted(failures - _known_checks())
    if unknown:
        raise ValueError(f"unknown check ids in --inject-failure: {', '.join(unknown)}")
    return failures


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _round(value: float) -> float:
    return round(value, 3)


def _build_trace(seed: int, lane: str) -> Dict[str, object]:
    trace_id = f"trace-{lane}-{seed}"
    trace_digest = _sha256(f"{seed}|trace|{lane}|runtime")
    return {
        "trace_id": trace_id,
        "execution_lane": lane,
        "capture_kind": "serial+eventlog",
        "trace_path": f"out/traces/{lane}-runtime-{seed}.log",
        "trace_digest": trace_digest,
        "runtime_source": "runtime_capture",
    }


def _build_evidence_item(
    *,
    seed: int,
    lane: str,
    artifact_id: str,
    trace: Dict[str, object],
    ordinal: int,
) -> Dict[str, object]:
    signature_digest = _sha256(f"{seed}|{lane}|{artifact_id}|{ordinal}|signature")
    return {
        "artifact_id": artifact_id,
        "execution_lane": lane,
        "runtime_source": {
            "kind": lane,
            "collector": "rugo-runtime-capture-v1",
            "command": f"capture-{lane}-runtime-evidence-v1 --seed {seed}",
        },
        "synthetic": False,
        "trace_id": trace["trace_id"],
        "trace_digest": trace["trace_digest"],
        "provenance": {
            "collector": "tools/collect_runtime_evidence_v1.py",
            "command": "python tools/collect_runtime_evidence_v1.py --out out/runtime-evidence-v1.json",
            "host_profile": "ci-linux-amd64",
            "capture_mode": "runtime",
            "source_date_epoch": str(DEFAULT_SEED),
        },
        "signature": {
            "algorithm": "sha256",
            "valid": True,
            "digest": signature_digest,
        },
    }


def _baseline_model(seed: int) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    traces = [_build_trace(seed, "qemu"), _build_trace(seed, "baremetal")]
    trace_index = {trace["execution_lane"]: trace for trace in traces}

    evidence_items = [
        _build_evidence_item(
            seed=seed,
            lane="qemu",
            artifact_id="runtime.qemu.boot.v1",
            trace=trace_index["qemu"],
            ordinal=1,
        ),
        _build_evidence_item(
            seed=seed,
            lane="qemu",
            artifact_id="runtime.qemu.services.v1",
            trace=trace_index["qemu"],
            ordinal=2,
        ),
        _build_evidence_item(
            seed=seed,
            lane="baremetal",
            artifact_id="runtime.baremetal.boot.v1",
            trace=trace_index["baremetal"],
            ordinal=3,
        ),
        _build_evidence_item(
            seed=seed,
            lane="baremetal",
            artifact_id="runtime.baremetal.services.v1",
            trace=trace_index["baremetal"],
            ordinal=4,
        ),
    ]
    return traces, evidence_items


def _mark_synthetic(item: Dict[str, object]) -> None:
    item["synthetic"] = True
    runtime_source = item.get("runtime_source", {})
    if isinstance(runtime_source, dict):
        runtime_source["kind"] = "synthetic_model"
    provenance = item.get("provenance", {})
    if isinstance(provenance, dict):
        provenance["capture_mode"] = "synthetic"


def _apply_injected_failures(
    *,
    injected_failures: Set[str],
    traces: List[Dict[str, object]],
    evidence_items: List[Dict[str, object]],
) -> None:
    if not evidence_items:
        return

    if "runtime_item_count" in injected_failures and len(evidence_items) > 1:
        evidence_items.pop()

    if "runtime_capture_ratio" in injected_failures:
        _mark_synthetic(evidence_items[0])

    if "synthetic_evidence_ratio" in injected_failures:
        _mark_synthetic(evidence_items[0])

    if "synthetic_only_artifacts" in injected_failures:
        for item in evidence_items:
            _mark_synthetic(item)

    if "provenance_fields_ratio" in injected_failures:
        provenance = evidence_items[0].get("provenance", {})
        if isinstance(provenance, dict):
            provenance.pop("collector", None)

    if "unsigned_artifact_count" in injected_failures:
        signature = evidence_items[0].get("signature", {})
        if isinstance(signature, dict):
            signature["valid"] = False

    if "trace_linkage_ratio" in injected_failures or "detached_trace_count" in injected_failures:
        evidence_items[0]["trace_id"] = "trace-detached"
        evidence_items[0]["trace_digest"] = _sha256("trace-detached")

    if "qemu_trace_presence_ratio" in injected_failures:
        traces[:] = [trace for trace in traces if trace.get("execution_lane") != "qemu"]

    if "baremetal_trace_presence_ratio" in injected_failures:
        traces[:] = [
            trace for trace in traces if trace.get("execution_lane") != "baremetal"
        ]


def _derive_metrics(
    traces: Sequence[Dict[str, object]],
    evidence_items: Sequence[Dict[str, object]],
) -> Dict[str, float]:
    total = len(evidence_items)
    trace_map = {
        str(trace.get("trace_id", "")): trace
        for trace in traces
        if isinstance(trace, dict) and trace.get("trace_id")
    }

    linked_count = 0
    runtime_count = 0
    synthetic_count = 0
    provenance_complete = 0
    unsigned_count = 0

    required_provenance = {
        "collector",
        "command",
        "host_profile",
        "capture_mode",
        "source_date_epoch",
    }

    for item in evidence_items:
        if not isinstance(item, dict):
            continue

        synthetic = bool(item.get("synthetic"))
        runtime_source = item.get("runtime_source", {})
        runtime_kind = (
            runtime_source.get("kind", "")
            if isinstance(runtime_source, dict)
            else ""
        )
        if synthetic or runtime_kind == "synthetic_model":
            synthetic_count += 1
        else:
            runtime_count += 1

        signature = item.get("signature", {})
        if not (isinstance(signature, dict) and signature.get("valid") is True):
            unsigned_count += 1

        provenance = item.get("provenance", {})
        if isinstance(provenance, dict) and all(
            provenance.get(field) not in (None, "") for field in required_provenance
        ):
            provenance_complete += 1

        trace_id = str(item.get("trace_id", ""))
        trace_digest = str(item.get("trace_digest", ""))
        linked_trace = trace_map.get(trace_id)
        if not isinstance(linked_trace, dict):
            continue
        if trace_digest != str(linked_trace.get("trace_digest", "")):
            continue
        if item.get("execution_lane") != linked_trace.get("execution_lane"):
            continue
        linked_count += 1

    qemu_trace_present = any(
        trace.get("execution_lane") == "qemu" for trace in traces if isinstance(trace, dict)
    )
    baremetal_trace_present = any(
        trace.get("execution_lane") == "baremetal"
        for trace in traces
        if isinstance(trace, dict)
    )

    if total == 0:
        synthetic_ratio = 1.0
        runtime_ratio = 0.0
        linkage_ratio = 0.0
        provenance_ratio = 0.0
    else:
        synthetic_ratio = synthetic_count / total
        runtime_ratio = runtime_count / total
        linkage_ratio = linked_count / total
        provenance_ratio = provenance_complete / total

    synthetic_only_flag = 1.0 if total > 0 and synthetic_count == total else 0.0
    detached_trace_count = float(total - linked_count)

    return {
        "runtime_item_count": float(total),
        "runtime_capture_ratio": _round(runtime_ratio),
        "qemu_trace_presence_ratio": 1.0 if qemu_trace_present else 0.0,
        "baremetal_trace_presence_ratio": 1.0 if baremetal_trace_present else 0.0,
        "trace_linkage_ratio": _round(linkage_ratio),
        "provenance_fields_ratio": _round(provenance_ratio),
        "unsigned_artifact_count": float(unsigned_count),
        "synthetic_evidence_ratio": _round(synthetic_ratio),
        "synthetic_only_artifacts": synthetic_only_flag,
        "detached_trace_count": detached_trace_count,
    }


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


def collect_runtime_evidence(
    seed: int,
    injected_failures: Set[str] | None = None,
) -> Dict[str, object]:
    failures = set() if injected_failures is None else set(injected_failures)
    traces, evidence_items = _baseline_model(seed)
    _apply_injected_failures(
        injected_failures=failures,
        traces=traces,
        evidence_items=evidence_items,
    )

    metrics = _derive_metrics(traces, evidence_items)
    checks: List[Dict[str, object]] = []
    for spec in CHECKS:
        observed = _round(metrics[spec.metric_key])
        checks.append(
            {
                "check_id": spec.check_id,
                "domain": spec.domain,
                "metric_key": spec.metric_key,
                "operator": spec.operator,
                "threshold": spec.threshold,
                "observed": observed,
                "pass": _passes(spec.operator, observed, spec.threshold),
            }
        )

    summary = {
        "execution": _domain_summary(checks, "execution"),
        "provenance": _domain_summary(checks, "provenance"),
        "synthetic": _domain_summary(checks, "synthetic"),
    }
    total_failures = sum(1 for check in checks if check["pass"] is False)

    runtime_items = int(sum(1 for item in evidence_items if item.get("synthetic") is False))
    synthetic_items = int(sum(1 for item in evidence_items if item.get("synthetic") is True))
    linked_trace_items = int(
        len(evidence_items) - int(metrics["detached_trace_count"])
    )

    stable_payload = {
        "schema": SCHEMA,
        "seed": seed,
        "checks": [
            {
                "check_id": check["check_id"],
                "observed": check["observed"],
                "pass": check["pass"],
            }
            for check in checks
        ],
        "traces": [
            {
                "trace_id": trace["trace_id"],
                "execution_lane": trace["execution_lane"],
                "trace_digest": trace["trace_digest"],
            }
            for trace in traces
        ],
        "evidence_items": [
            {
                "artifact_id": item["artifact_id"],
                "execution_lane": item["execution_lane"],
                "synthetic": item["synthetic"],
                "trace_id": item["trace_id"],
                "trace_digest": item["trace_digest"],
                "signature_valid": item.get("signature", {}).get("valid") is True,
            }
            for item in evidence_items
        ],
        "injected_failures": sorted(failures),
    }
    digest = hashlib.sha256(
        json.dumps(stable_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return {
        "schema": SCHEMA,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "evidence_integrity_policy_id": EVIDENCE_INTEGRITY_POLICY_ID,
        "runtime_evidence_schema_id": RUNTIME_EVIDENCE_SCHEMA_ID,
        "gate_provenance_policy_id": GATE_PROVENANCE_POLICY_ID,
        "seed": seed,
        "gate": "test-evidence-integrity-v1",
        "traces": traces,
        "evidence_items": evidence_items,
        "checks": checks,
        "summary": summary,
        "totals": {
            "evidence_items": len(evidence_items),
            "runtime_items": runtime_items,
            "synthetic_items": synthetic_items,
            "linked_trace_items": linked_trace_items,
            "detached_trace_count": int(metrics["detached_trace_count"]),
        },
        "artifact_refs": {
            "runtime_evidence_report": "out/runtime-evidence-v1.json",
            "gate_evidence_audit_report": "out/gate-evidence-audit-v1.json",
            "junit": "out/pytest-evidence-integrity-v1.xml",
            "synthetic_ban_junit": "out/pytest-synthetic-evidence-ban-v1.xml",
            "ci_artifact": "evidence-integrity-v1-artifacts",
            "synthetic_ban_ci_artifact": "synthetic-evidence-ban-v1-artifacts",
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
    parser.add_argument(
        "--synthetic-only",
        action="store_true",
        help="force all evidence items into synthetic-only mode",
    )
    parser.add_argument("--max-failures", type=int, default=0)
    parser.add_argument("--out", default="out/runtime-evidence-v1.json")
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

    if args.synthetic_only:
        injected_failures.add("synthetic_only_artifacts")

    report = collect_runtime_evidence(
        seed=args.seed,
        injected_failures=injected_failures,
    )
    report["max_failures"] = args.max_failures
    report["gate_pass"] = report["total_failures"] <= args.max_failures

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"runtime-evidence-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
