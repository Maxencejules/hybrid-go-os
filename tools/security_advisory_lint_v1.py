#!/usr/bin/env python3
"""Validate security advisory schema and required fields."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


REQUIRED_FIELDS = [
    "advisory_id",
    "severity",
    "cve_ids",
    "affected_versions",
    "fixed_versions",
    "published_utc",
]

ALLOWED_SEVERITIES = {"critical", "high", "medium", "low"}
POLICY_ID = "rugo.security_advisory_policy.v1"


def _default_advisory() -> Dict[str, object]:
    return {
        "advisory_id": "RUGO-2026-0001",
        "severity": "high",
        "cve_ids": ["CVE-2026-00001"],
        "affected_versions": ["1.0.0"],
        "fixed_versions": ["1.0.1"],
        "published_utc": "2026-03-09T00:00:00Z",
    }


def _is_rfc3339_utc(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True


def lint_advisory(advisory: Dict[str, object]) -> Dict[str, object]:
    errors: List[str] = []
    for field in REQUIRED_FIELDS:
        if field not in advisory:
            errors.append(f"missing_field:{field}")

    severity = str(advisory.get("severity", "")).lower()
    if severity not in ALLOWED_SEVERITIES:
        errors.append(f"invalid_severity:{severity}")

    cve_ids = advisory.get("cve_ids", [])
    if not isinstance(cve_ids, list) or not cve_ids:
        errors.append("invalid_cve_ids")
    else:
        for cve in cve_ids:
            if not str(cve).startswith("CVE-"):
                errors.append(f"invalid_cve_id:{cve}")

    affected_versions = advisory.get("affected_versions", [])
    if not isinstance(affected_versions, list) or not affected_versions:
        errors.append("invalid_affected_versions")

    fixed_versions = advisory.get("fixed_versions", [])
    if not isinstance(fixed_versions, list) or not fixed_versions:
        errors.append("invalid_fixed_versions")

    published_utc = advisory.get("published_utc")
    if not _is_rfc3339_utc(published_utc):
        errors.append("invalid_published_utc")

    return {
        "schema": "rugo.security_advisory_lint_report.v1",
        "policy_id": POLICY_ID,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "required_fields": REQUIRED_FIELDS,
        "total_errors": len(errors),
        "errors": errors,
        "valid": len(errors) == 0,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--advisory", default="")
    p.add_argument("--out", default="out/security-advisory-lint-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.advisory:
        advisory = json.loads(Path(args.advisory).read_text(encoding="utf-8"))
    else:
        advisory = _default_advisory()
    report = lint_advisory(advisory)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"security-advisory-lint: {out_path}")
    print(f"valid: {report['valid']}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
