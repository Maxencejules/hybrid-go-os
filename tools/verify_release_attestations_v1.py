#!/usr/bin/env python3
"""Verify release attestation continuity and policy drift thresholds."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--expected-policy-id", default="release-attestation-v1")
    p.add_argument("--observed-policy-id", default="release-attestation-v1")
    p.add_argument("--observed-drift", type=int, default=0)
    p.add_argument("--max-drift", type=int, default=0)
    p.add_argument("--out", default="out/release-attestation-verification-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    policy_match = args.expected_policy_id == args.observed_policy_id
    meets_drift = args.observed_drift <= args.max_drift
    report = {
        "schema": "rugo.release_attestation_verification.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "expected_policy_id": args.expected_policy_id,
        "observed_policy_id": args.observed_policy_id,
        "policy_match": policy_match,
        "drift_count": args.observed_drift,
        "max_drift": args.max_drift,
        "meets_target": policy_match and meets_drift,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"release-attestation-verification: {out_path}")
    print(f"meets_target: {report['meets_target']}")
    return 0 if report["meets_target"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

