#!/usr/bin/env python3
"""Emit release policy/channel contract artifact for M14."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


SCHEMA = "rugo.release_contract.v1"
CHANNELS = {
    "nightly": {
        "cadence": "daily",
        "support_days": 7,
        "compatibility": "no compatibility guarantees",
    },
    "beta": {
        "cadence": "weekly",
        "support_days": 30,
        "compatibility": "feature-frozen except release blockers",
    },
    "stable": {
        "cadence": "manual promotion",
        "support_days": 90,
        "compatibility": "no ABI/profile break in stable line",
    },
}


def build_contract(channel: str, version: str, build_sequence: int) -> Dict[str, object]:
    if channel not in CHANNELS:
        raise ValueError(f"unsupported channel: {channel}")
    if build_sequence <= 0:
        raise ValueError("build_sequence must be > 0")

    return {
        "schema": SCHEMA,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "version": version,
        "build_sequence": build_sequence,
        "selected_channel": channel,
        "channels": CHANNELS,
        "lts_policy": {
            "selection_rule": "every second stable release",
            "support_months": 12,
        },
        "backport_classes": [
            "security_fix",
            "crash_or_data_loss_fix",
            "release_blocker_fix",
        ],
        "required_artifacts": [
            "out/release-contract-v1.json",
            "out/update-attack-suite-v1.json",
            "out/sbom-v1.spdx.json",
            "out/provenance-v1.json",
        ],
        "owners": {
            "release_owner": "release-owner",
            "update_pipeline_owner": "update-pipeline-owner",
            "security_owner": "security-owner",
            "doc_owner": "doc-owner",
        },
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--channel", default="stable", choices=sorted(CHANNELS.keys()))
    p.add_argument("--version", default="1.0.0")
    p.add_argument("--build-sequence", type=int, default=1)
    p.add_argument("--out", default="out/release-contract-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    report = build_contract(
        channel=args.channel,
        version=args.version,
        build_sequence=args.build_sequence,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"release-contract: {out_path}")
    print(f"selected_channel: {report['selected_channel']}")
    print(f"version: {report['version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
