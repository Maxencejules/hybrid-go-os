#!/usr/bin/env python3
"""Build deterministic installer contract artifact for M20."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def build_installer_contract(channel: str, version: str, build_sequence: int) -> Dict[str, object]:
    return {
        "schema": "rugo.installer_contract.v2",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "selected_channel": channel,
        "version": version,
        "build_sequence": build_sequence,
        "preflight_checks": [
            "sha256",
            "free_space",
            "metadata_presence",
        ],
        "installer_profile": {
            "mode": "offline-first",
            "bootloader": "limine",
            "partition_layout": ["efi", "system", "recovery"],
            "required_artifacts": [
                "out/os.iso",
                "out/release-contract-v1.json",
            ],
        },
        "recovery_profile": {
            "rollback_supported": True,
            "rollback_source": "last-trusted-sequence",
            "support_bundle_tool": "tools/collect_support_bundle_v2.py",
        },
        "required_outputs": [
            "out/installer-v2.json",
            "out/upgrade-recovery-v2.json",
            "out/support-bundle-v2.json",
        ],
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--channel", default="stable")
    p.add_argument("--version", default="2.0.0")
    p.add_argument("--build-sequence", type=int, default=1)
    p.add_argument("--out", default="out/installer-v2.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.build_sequence <= 0:
        print("build_sequence must be > 0")
        return 1

    contract = build_installer_contract(
        channel=args.channel,
        version=args.version,
        build_sequence=args.build_sequence,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    print(f"installer-contract: {out_path}")
    print(f"build_sequence: {contract['build_sequence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
