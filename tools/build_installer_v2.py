#!/usr/bin/env python3
"""Build deterministic installer contract artifact for M20."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import release_bundle_v1 as release_bundle


def build_installer_contract(
    channel: str,
    version: str,
    build_sequence: int,
    bundle: Dict[str, object] | None = None,
    install_state_path: str = "",
) -> Dict[str, object]:
    contract = {
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
                "out/release-bundle-v1.json",
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
            "out/install-state-v1.json",
            "out/upgrade-recovery-v2.json",
            "out/support-bundle-v2.json",
        ],
    }
    if bundle is not None:
        installer_artifact = release_bundle.artifact_by_role(bundle, "installer_image")
        recovery_artifact = release_bundle.artifact_by_role(bundle, "recovery_image")
        system_artifact = release_bundle.artifact_by_role(bundle, "system_image")
        contract["release_bundle_path"] = release_bundle.DEFAULT_BUNDLE_PATH.as_posix()
        contract["release_bundle_digest"] = bundle.get("digest", "")
        contract["installer_profile"]["bootable_media"] = {
            "system_image": {
                "path": system_artifact["path"],
                "sha256": system_artifact["sha256"],
            },
            "installer_image": {
                "path": installer_artifact["path"],
                "sha256": installer_artifact["sha256"],
            },
        }
        contract["recovery_profile"]["recovery_media"] = {
            "path": recovery_artifact["path"],
            "sha256": recovery_artifact["sha256"],
        }
        contract["runtime_capture"] = dict(bundle.get("runtime_capture", {}))
    if install_state_path:
        contract["persisted_install_manifest"] = install_state_path
    return contract


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--channel", default="stable")
    p.add_argument("--version", default="2.0.0")
    p.add_argument("--build-sequence", type=int, default=1)
    p.add_argument("--release-bundle", default="")
    p.add_argument("--install-state-out", default=str(release_bundle.DEFAULT_INSTALL_STATE_PATH))
    p.add_argument("--out", default="out/installer-v2.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.build_sequence <= 0:
        print("build_sequence must be > 0")
        return 1

    bundle = None
    if args.release_bundle:
        bundle = release_bundle.load_bundle(Path(args.release_bundle))

    contract = build_installer_contract(
        channel=args.channel,
        version=args.version,
        build_sequence=args.build_sequence,
        bundle=bundle,
        install_state_path=Path(args.install_state_out).as_posix(),
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")

    if bundle is not None:
        install_state = release_bundle.build_install_state(
            bundle=bundle,
            bundle_path=Path(args.release_bundle).as_posix(),
        )
        release_bundle.write_install_state(Path(args.install_state_out), install_state)
    print(f"installer-contract: {out_path}")
    print(f"build_sequence: {contract['build_sequence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
