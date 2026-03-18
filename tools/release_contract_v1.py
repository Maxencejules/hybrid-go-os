#!/usr/bin/env python3
"""Emit release policy/channel contract artifact for M14."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import release_bundle_v1 as release_bundle


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


def build_contract(
    channel: str,
    version: str,
    build_sequence: int,
    bundle: Dict[str, object] | None = None,
) -> Dict[str, object]:
    if channel not in CHANNELS:
        raise ValueError(f"unsupported channel: {channel}")
    if build_sequence <= 0:
        raise ValueError("build_sequence must be > 0")

    report = {
        "schema": SCHEMA,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "version": version,
        "build_sequence": build_sequence,
        "version_build": release_bundle.version_build(version, build_sequence),
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
            "out/release-bundle-v1.json",
            "out/release-contract-v1.json",
            "out/update-attack-suite-v1.json",
            "out/sbom-v1.spdx.json",
            "out/provenance-v1.json",
        ],
        "attestation_policy_id": "release-attestation-v1",
        "owners": {
            "release_owner": "release-owner",
            "update_pipeline_owner": "update-pipeline-owner",
            "security_owner": "security-owner",
            "doc_owner": "doc-owner",
        },
    }
    if bundle is not None:
        report["default_lane_release"] = {
            "schema": bundle.get("schema"),
            "release_dir": bundle.get("release_dir"),
            "release_bundle_digest": bundle.get("digest"),
            "source_lane": bundle.get("source_lane"),
            "execution_lane": bundle.get("execution_lane"),
            "runtime_capture": dict(bundle.get("runtime_capture", {})),
            "release_notes": dict(bundle.get("release_notes", {})),
            "bootable_artifacts": [
                {
                    "role": artifact.get("role"),
                    "path": artifact.get("path"),
                    "sha256": artifact.get("sha256"),
                    "size": artifact.get("size"),
                }
                for artifact in bundle.get("artifacts", [])
                if isinstance(artifact, dict) and artifact.get("bootable") is True
            ],
        }
        report["required_artifacts"].extend(
            artifact["path"]
            for artifact in report["default_lane_release"]["bootable_artifacts"]
        )
    return report


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--channel", default="stable", choices=sorted(CHANNELS.keys()))
    p.add_argument("--version", default="1.0.0")
    p.add_argument("--build-sequence", type=int, default=1)
    p.add_argument("--release-bundle", default="")
    p.add_argument("--out", default="out/release-contract-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    bundle = None
    if args.release_bundle:
        bundle = release_bundle.load_bundle(Path(args.release_bundle))
    report = build_contract(
        channel=args.channel,
        version=args.version,
        build_sequence=args.build_sequence,
        bundle=bundle,
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
