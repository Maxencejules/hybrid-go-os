#!/usr/bin/env python3
"""Audit release branch policy compliance for M31 lifecycle gate."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


SCHEMA = "rugo.release_branch_audit.v2"
POLICY_ID = "rugo.release_policy.v2"
RELEASE_BRANCH_RE = re.compile(r"^release/\d+\.\d+$")
HOTFIX_BRANCH_RE = re.compile(r"^hotfix/\d+\.\d+\.\d+$")
DEFAULT_BRANCHES = ["release/1.0", "release/1.1", "hotfix/1.1.1"]
DEFAULT_REQUIRED_BRANCHES = ["release/1.0", "release/1.1"]


def run_audit(
    branches: List[str],
    required_branches: List[str],
    allow_hotfix: bool,
) -> Dict[str, object]:
    unique_branches = list(dict.fromkeys(branches))
    required = list(dict.fromkeys(required_branches))

    invalid_branches: List[str] = []
    hotfix_branches: List[str] = []
    for branch in unique_branches:
        if RELEASE_BRANCH_RE.fullmatch(branch):
            continue
        if HOTFIX_BRANCH_RE.fullmatch(branch):
            hotfix_branches.append(branch)
            continue
        invalid_branches.append(branch)

    missing_required = [branch for branch in required if branch not in unique_branches]
    release_branches = [b for b in unique_branches if RELEASE_BRANCH_RE.fullmatch(b)]

    checks = [
        {
            "name": "branch_set_non_empty",
            "pass": len(unique_branches) > 0,
        },
        {
            "name": "branch_naming_compliant",
            "pass": len(invalid_branches) == 0,
        },
        {
            "name": "required_branches_present",
            "pass": len(missing_required) == 0,
        },
        {
            "name": "release_branch_present",
            "pass": len(release_branches) > 0,
        },
        {
            "name": "hotfix_branch_policy",
            "pass": allow_hotfix or len(hotfix_branches) == 0,
        },
    ]
    total_failures = sum(1 for check in checks if check["pass"] is False)

    return {
        "schema": SCHEMA,
        "policy_id": POLICY_ID,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "allow_hotfix": allow_hotfix,
        "branches": unique_branches,
        "required_branches": required,
        "release_branches": release_branches,
        "hotfix_branches": hotfix_branches,
        "missing_required_branches": missing_required,
        "invalid_branches": invalid_branches,
        "checks": checks,
        "total_failures": total_failures,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch", action="append", default=[])
    parser.add_argument("--required-branch", action="append", default=[])
    parser.add_argument(
        "--disallow-hotfix",
        action="store_true",
        help="treat hotfix/* branches as policy violations",
    )
    parser.add_argument("--max-failures", type=int, default=0)
    parser.add_argument("--out", default="out/release-branch-audit-v2.json")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    branches = args.branch or list(DEFAULT_BRANCHES)
    required = args.required_branch or list(DEFAULT_REQUIRED_BRANCHES)
    report = run_audit(
        branches=branches,
        required_branches=required,
        allow_hotfix=not args.disallow_hotfix,
    )
    report["max_failures"] = args.max_failures
    report["meets_target"] = report["total_failures"] <= args.max_failures

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"release-branch-audit: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    return 0 if report["meets_target"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
