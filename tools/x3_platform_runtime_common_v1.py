#!/usr/bin/env python3
"""Shared helpers for X3 runtime-backed platform and ecosystem closure."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Set

import check_update_trust_v1
import pkg_rebuild_verify_v3
import repo_policy_check_v3
import run_app_catalog_sim_v1
import run_pkg_install_success_campaign_v1
import run_platform_feature_conformance_v1
import run_reproducible_catalog_audit_v1
import run_storage_feature_campaign_v1
import runtime_capture_common_v1 as runtime_capture


SCHEMA = "rugo.x3_platform_ecosystem_runtime_report.v1"
POLICY_ID = "rugo.x3_platform_ecosystem_runtime_qualification.v1"
TRACK_ID = "X3"
DEFAULT_SEED = 20260318
DEFAULT_RUNTIME_CAPTURE_PATH = Path("out/booted-runtime-v1.json")

SUPPORTING_REPORT_PATHS = {
    "repo_policy_v3": "out/repo-policy-v3.json",
    "pkg_rebuild_v3": "out/pkg-rebuild-v3.json",
    "update_trust_v1": "out/update-trust-v1.json",
    "storage_feature_v1": "out/storage-feature-v1.json",
    "platform_feature_v1": "out/platform-feature-v1.json",
    "app_catalog_v1": "out/app-catalog-sim-v1.json",
    "pkg_install_success_v1": "out/pkg-install-success-v1.json",
    "catalog_audit_v1": "out/catalog-audit-v1.json",
}


@dataclass(frozen=True)
class RuntimeCheck:
    check_id: str
    domain: str
    cold_markers: Sequence[str]
    replay_markers: Sequence[str]
    description: str


RUNTIME_CHECKS: Sequence[RuntimeCheck] = (
    RuntimeCheck(
        check_id="pkgsvc_lifecycle",
        domain="package_update",
        cold_markers=("PKGSVC: start", "PKGSVC: ready", "GOSH: pkg ok", "PKGSVC: stop"),
        replay_markers=("PKGSVC: start", "PKGSVC: ready", "GOSH: pkg ok", "PKGSVC: stop"),
        description="package service is started, consumed by shell, and cleanly stopped",
    ),
    RuntimeCheck(
        check_id="metadata_rotation",
        domain="package_update",
        cold_markers=("UPD3: metadata ok",),
        replay_markers=("UPD3: rotate ok", "UPD3: metadata ok", "UPD3: apply ok"),
        description="signed metadata is verified and key rotation is exercised on replay boot",
    ),
    RuntimeCheck(
        check_id="catalog_distribution",
        domain="catalog_distribution",
        cold_markers=("CAT3: catalog ok", "CAT3: install base ok", "CAT3: install net ok", "CAT3: telemetry ok"),
        replay_markers=("CAT3: catalog ok", "CAT3: stage ok", "CAT3: install media ok", "CAT3: telemetry ok", "UPD3: rollback ok"),
        description="catalog, staged promotion, install telemetry, and rollback-safe workflow are visible on the booted lane",
    ),
    RuntimeCheck(
        check_id="storage_platform",
        domain="storage_platform",
        cold_markers=("STORX3: snapshot ok", "STORX3: xattr ok", "STORX3: cap ok"),
        replay_markers=("STORX3: resize ok", "STORX3: reflink ok", "STORX3: xattr ok", "STORX3: cap ok"),
        description="snapshot, resize, reflink, xattr, and capability negotiation are exercised by the live package lane",
    ),
)


def _known_checks() -> Set[str]:
    return {check.check_id for check in RUNTIME_CHECKS} | {"pkgsvc_isolation"}


def normalize_failures(values: Sequence[str]) -> Set[str]:
    failures = {value.strip() for value in values if value.strip()}
    unknown = sorted(failures - _known_checks())
    if unknown:
        raise ValueError(f"unknown check ids in --inject-failure: {', '.join(unknown)}")
    return failures


def collect_source_reports(seed: int) -> Dict[str, Dict[str, object]]:
    storage_feature = run_storage_feature_campaign_v1.run_campaign(seed=20260309)
    platform_feature = run_platform_feature_conformance_v1.run_conformance(seed=20260309)
    return {
        "repo_policy_v3": repo_policy_check_v3.run_policy_check(),
        "pkg_rebuild_v3": pkg_rebuild_verify_v3.run_rebuild(seed=20260309),
        "update_trust_v1": check_update_trust_v1.run_suite(),
        "storage_feature_v1": storage_feature,
        "platform_feature_v1": platform_feature,
        "app_catalog_v1": run_app_catalog_sim_v1.run_simulation(seed=20260309),
        "pkg_install_success_v1": run_pkg_install_success_campaign_v1.run_campaign(seed=20260309),
        "catalog_audit_v1": run_reproducible_catalog_audit_v1.run_audit(seed=20260309),
    }


def write_supporting_reports(
    reports: Mapping[str, Dict[str, object]],
    *,
    base_dir: str | Path,
) -> None:
    root = Path(base_dir)
    root.mkdir(parents=True, exist_ok=True)
    for key, relpath in SUPPORTING_REPORT_PATHS.items():
        runtime_capture.write_json(root / Path(relpath).name, reports[key])


def load_runtime_capture(
    *,
    runtime_capture_path: str | Path | None = None,
    fixture: bool = False,
) -> Dict[str, object]:
    if fixture:
        return runtime_capture.build_fixture_capture()
    path = DEFAULT_RUNTIME_CAPTURE_PATH if runtime_capture_path is None else Path(runtime_capture_path)
    if path.is_file():
        return runtime_capture.read_json(Path(path))
    return runtime_capture.build_fixture_capture()


def _boot_by_profile(capture: Dict[str, object], profile: str) -> Dict[str, object]:
    for boot in runtime_capture.iter_boots(capture):
        if boot.get("boot_profile") == profile:
            return boot
    raise KeyError(f"missing boot profile: {profile}")


def _markers_present(boot: Dict[str, object], markers: Sequence[str]) -> bool:
    return all(runtime_capture.find_first_line_ts(boot, marker) is not None for marker in markers)


def _pkgsvc_isolation_ok(capture: Dict[str, object]) -> bool:
    for boot in runtime_capture.iter_boots(capture):
        snapshot = runtime_capture.latest_task_snapshot(boot, "pkgsvc")
        if snapshot is None:
            return False
        metrics = snapshot.get("metrics", {})
        if not isinstance(metrics, dict):
            return False
        if metrics.get("dom") != 4:
            return False
        if metrics.get("cap") != 1:
            return False
        if metrics.get("fd") != 0:
            return False
        if metrics.get("sock") != 0:
            return False
        if metrics.get("ep") != 1:
            return False
    return True


def _summary_for(checks: Sequence[Dict[str, object]], domain: str) -> Dict[str, object]:
    scoped = [check for check in checks if check["domain"] == domain]
    failures = [check for check in scoped if check["pass"] is False]
    return {
        "checks": len(scoped),
        "failures": len(failures),
        "pass": len(failures) == 0,
    }


def _support_report_pass(report: Mapping[str, object], failure_key: str) -> bool:
    value = report.get(failure_key, 0)
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 0
    return False


def _backlog_rows(
    checks: Sequence[Dict[str, object]],
    reports: Mapping[str, Dict[str, object]],
) -> List[Dict[str, object]]:
    check_map = {check["check_id"]: check for check in checks}
    m26_pass = (
        check_map["pkgsvc_lifecycle"]["pass"]
        and check_map["metadata_rotation"]["pass"]
        and check_map["pkgsvc_isolation"]["pass"]
        and _support_report_pass(reports["repo_policy_v3"], "total_failures")
        and _support_report_pass(reports["pkg_rebuild_v3"], "total_mismatches")
        and _support_report_pass(reports["update_trust_v1"], "total_failures")
    )
    m38_pass = (
        check_map["storage_platform"]["pass"]
        and _support_report_pass(reports["storage_feature_v1"], "total_failures")
        and _support_report_pass(reports["platform_feature_v1"], "total_failures")
    )
    m39_pass = (
        check_map["catalog_distribution"]["pass"]
        and _support_report_pass(reports["app_catalog_v1"], "total_failures")
        and _support_report_pass(reports["pkg_install_success_v1"], "total_failures")
        and _support_report_pass(reports["catalog_audit_v1"], "total_failures")
    )
    return [
        {
            "backlog": "M26",
            "title": "Package/Repo Ecosystem v3",
            "runtime_class": "Runtime-backed",
            "status": "pass" if m26_pass else "fail",
            "required_checks": ["pkgsvc_lifecycle", "metadata_rotation", "pkgsvc_isolation"],
            "required_reports": ["repo_policy_v3", "pkg_rebuild_v3", "update_trust_v1"],
        },
        {
            "backlog": "M38",
            "title": "Storage + Platform Feature Expansion v1",
            "runtime_class": "Runtime-backed",
            "status": "pass" if m38_pass else "fail",
            "required_checks": ["storage_platform"],
            "required_reports": ["storage_feature_v1", "platform_feature_v1"],
        },
        {
            "backlog": "M39",
            "title": "Ecosystem Scale + Distribution Workflow v1",
            "runtime_class": "Runtime-backed",
            "status": "pass" if m39_pass else "fail",
            "required_checks": ["catalog_distribution"],
            "required_reports": ["app_catalog_v1", "pkg_install_success_v1", "catalog_audit_v1"],
        },
    ]


def build_report(
    *,
    seed: int,
    capture: Dict[str, object],
    reports: Mapping[str, Dict[str, object]],
    injected_failures: Set[str] | None = None,
) -> Dict[str, object]:
    failures = set() if injected_failures is None else set(injected_failures)
    cold = _boot_by_profile(capture, "cold_boot")
    replay = _boot_by_profile(capture, "replay_boot")

    checks: List[Dict[str, object]] = []
    for spec in RUNTIME_CHECKS:
        passed = _markers_present(cold, spec.cold_markers) and _markers_present(replay, spec.replay_markers)
        if spec.check_id in failures:
            passed = False
        checks.append(
            {
                "check_id": spec.check_id,
                "domain": spec.domain,
                "description": spec.description,
                "cold_markers": list(spec.cold_markers),
                "replay_markers": list(spec.replay_markers),
                "pass": passed,
            }
        )

    isolation_pass = _pkgsvc_isolation_ok(capture)
    if "pkgsvc_isolation" in failures:
        isolation_pass = False
    checks.append(
        {
            "check_id": "pkgsvc_isolation",
            "domain": "package_update",
            "description": "pkgsvc runs with the declared storage-only isolation profile on every boot",
            "pass": isolation_pass,
            "required_metrics": {"dom": 4, "cap": 1, "fd": 0, "sock": 0, "ep": 1},
        }
    )

    backlog_closure = _backlog_rows(checks, reports)
    total_failures = sum(1 for check in checks if check["pass"] is False)
    total_failures += sum(1 for row in backlog_closure if row["status"] != "pass")

    summary = {
        "package_update": _summary_for(checks, "package_update"),
        "storage_platform": _summary_for(checks, "storage_platform"),
        "catalog_distribution": _summary_for(checks, "catalog_distribution"),
        "backlogs": {
            "runtime_backed": sum(1 for row in backlog_closure if row["status"] == "pass"),
            "total": len(backlog_closure),
        },
    }

    stable_payload = {
        "schema": SCHEMA,
        "capture_digest": capture.get("digest", ""),
        "seed": seed,
        "checks": [
            {"check_id": check["check_id"], "pass": check["pass"]}
            for check in checks
        ],
        "backlog_closure": [
            {"backlog": row["backlog"], "status": row["status"]}
            for row in backlog_closure
        ],
        "injected_failures": sorted(failures),
    }
    digest = runtime_capture.stable_digest(stable_payload)

    return {
        "schema": SCHEMA,
        "track_id": TRACK_ID,
        "policy_id": POLICY_ID,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed": seed,
        "gate": "test-x3-platform-runtime-v1",
        "capture": {
            "schema": capture.get("schema", ""),
            "capture_id": capture.get("capture_id", ""),
            "capture_mode": capture.get("capture_mode", ""),
            "trace_id": capture.get("trace_id", ""),
            "digest": capture.get("digest", ""),
        },
        "checks": checks,
        "summary": summary,
        "backlog_closure": backlog_closure,
        "source_reports": {key: {"schema": value.get("schema", ""), "digest": value.get("digest", "")} for key, value in reports.items()},
        "artifact_refs": {
            "runtime_capture": DEFAULT_RUNTIME_CAPTURE_PATH.as_posix(),
            "report": "out/x3-platform-runtime-v1.json",
            **SUPPORTING_REPORT_PATHS,
        },
        "injected_failures": sorted(failures),
        "failures": sorted(
            [check["check_id"] for check in checks if check["pass"] is False]
            + [row["backlog"] for row in backlog_closure if row["status"] != "pass"]
        ),
        "total_failures": total_failures,
        "gate_pass": total_failures == 0,
        "digest": digest,
    }
