#!/usr/bin/env python3
"""Revalidate SBOM/provenance alignment for release candidates."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import release_bundle_v1 as release_bundle


def _load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_check(
    sbom_path: Path,
    provenance_path: Path,
    release_bundle_path: Path | None = None,
) -> Dict[str, object]:
    checks: List[Dict[str, object]] = []

    if not sbom_path.is_file():
        checks.append({"name": "sbom_exists", "pass": False, "reason": "missing"})
        sbom = {}
    else:
        sbom = _load_json(sbom_path)
        checks.append({"name": "sbom_exists", "pass": True})
        checks.append(
            {
                "name": "sbom_schema",
                "pass": str(sbom.get("spdxVersion", "")).startswith("SPDX-"),
            }
        )

    if not provenance_path.is_file():
        checks.append({"name": "provenance_exists", "pass": False, "reason": "missing"})
        provenance = {}
    else:
        provenance = _load_json(provenance_path)
        checks.append({"name": "provenance_exists", "pass": True})
        checks.append(
            {
                "name": "provenance_schema",
                "pass": provenance.get("schema") == "rugo.provenance.v1",
            }
        )

    sbom_files = {f.get("fileName") for f in sbom.get("files", []) if isinstance(f, dict)}
    subjects = {
        s.get("name")
        for s in provenance.get("subjects", [])
        if isinstance(s, dict) and s.get("name") is not None
    }
    if subjects and sbom_files:
        checks.append(
            {
                "name": "subject_consistency",
                "pass": subjects.issubset(sbom_files),
            }
        )
    else:
        checks.append({"name": "subject_consistency", "pass": True})

    bundle = None
    if release_bundle_path is not None and release_bundle_path.is_file():
        bundle = release_bundle.load_bundle(release_bundle_path)
        checks.append({"name": "release_bundle_exists", "pass": True})
    elif release_bundle_path is not None:
        checks.append({"name": "release_bundle_exists", "pass": False, "reason": "missing"})

    if bundle is not None:
        bundle_paths = {
            path.as_posix()
            for path in release_bundle.artifact_paths(bundle)
            if path.is_file()
        }
        bundle_subjects_covered = bundle_paths.issubset(subjects) if subjects else False
        bundle_sbom_covered = bundle_paths.issubset(sbom_files) if sbom_files else False
        checks.append(
            {
                "name": "bundle_subject_coverage",
                "pass": bundle_subjects_covered,
            }
        )
        checks.append(
            {
                "name": "bundle_sbom_coverage",
                "pass": bundle_sbom_covered,
            }
        )

    total_failures = sum(1 for c in checks if not c["pass"])
    return {
        "schema": "rugo.supply_chain_revalidation_report.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "checks": checks,
        "total_failures": total_failures,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sbom", default="out/sbom-v1.spdx.json")
    p.add_argument("--provenance", default="out/provenance-v1.json")
    p.add_argument("--release-bundle", default="")
    p.add_argument("--max-failures", type=int, default=0)
    p.add_argument("--out", default="out/supply-chain-revalidation-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    report = run_check(
        sbom_path=Path(args.sbom),
        provenance_path=Path(args.provenance),
        release_bundle_path=Path(args.release_bundle) if args.release_bundle else None,
    )
    report["max_failures"] = args.max_failures
    report["meets_target"] = report["total_failures"] <= args.max_failures
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"supply-chain-revalidation: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    return 0 if report["meets_target"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
