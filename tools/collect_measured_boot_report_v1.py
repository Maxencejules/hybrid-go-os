#!/usr/bin/env python3
"""Generate measured-boot attestation report for M23."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_report(platform: str, pcrs: List[int], policy_profile: str) -> Dict[str, object]:
    required = {0, 2, 4, 7}
    pcr_set = set(pcrs)
    missing = sorted(required - pcr_set)
    event_log = [
        {"pcr": 0, "type": "firmware", "digest": _digest("firmware-v1")},
        {"pcr": 2, "type": "bootloader", "digest": _digest("bootloader-v1")},
        {"pcr": 4, "type": "kernel", "digest": _digest("kernel-v1")},
        {"pcr": 7, "type": "secure-config", "digest": _digest("secure-config-v1")},
    ]
    return {
        "schema": "rugo.measured_boot_report.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "platform": platform,
        "policy_profile": policy_profile,
        "pcrs": sorted(pcr_set),
        "tpm_event_log": event_log,
        "policy_pass": len(missing) == 0,
        "failures": [f"missing_pcr_{n}" for n in missing],
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--platform", default="qemu-q35")
    p.add_argument("--pcrs", default="0,2,4,7")
    p.add_argument("--policy-profile", default="firmware-attestation-v1")
    p.add_argument("--out", default="out/measured-boot-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    pcrs = [int(v.strip()) for v in args.pcrs.split(",") if v.strip()]
    report = build_report(platform=args.platform, pcrs=pcrs, policy_profile=args.policy_profile)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"measured-boot-report: {out_path}")
    print(f"policy_pass: {report['policy_pass']}")
    return 0 if report["policy_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

