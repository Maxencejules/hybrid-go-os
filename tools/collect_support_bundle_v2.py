#!/usr/bin/env python3
"""Collect deterministic support bundle metadata for M20."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import release_bundle_v1 as release_bundle


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def build_bundle(
    artifacts: List[Path],
    bundle: Dict[str, object] | None = None,
    install_state: Dict[str, object] | None = None,
) -> Dict[str, object]:
    evidence: List[Dict[str, object]] = []
    for path in artifacts:
        if not path.is_file():
            continue
        evidence.append(
            {
                "path": path.as_posix(),
                "size": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    return {
        "schema": "rugo.support_bundle.v2",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "triage": {
            "runbook": "docs/build/operations_runbook_v2.md",
            "requires_rollback_context": True,
            "required_artifacts": [
                "release-bundle-v1",
                "install-state-v1",
                "installer-v2",
                "upgrade-recovery-v2",
            ],
        },
        "release_context": {
            "release_bundle_digest": (bundle or {}).get("digest", ""),
            "runtime_capture_id": ((bundle or {}).get("runtime_capture") or {}).get(
                "capture_id", ""
            ),
            "active_slot": (install_state or {}).get("active_slot", ""),
            "trusted_floor_sequence": (install_state or {}).get(
                "trusted_floor_sequence", 0
            ),
        },
        "evidence": evidence,
        "redactions": [
            "no secrets captured in model-level bundle",
            "absolute host usernames omitted from output",
        ],
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--artifacts",
        nargs="*",
        default=[
            "out/installer-v2.json",
            "out/upgrade-recovery-v2.json",
        ],
    )
    p.add_argument("--release-bundle", default="")
    p.add_argument("--install-state", default="")
    p.add_argument("--out", default="out/support-bundle-v2.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    loaded_bundle = (
        release_bundle.load_bundle(Path(args.release_bundle))
        if args.release_bundle
        else None
    )
    install_state = (
        release_bundle.load_install_state(Path(args.install_state))
        if args.install_state
        else None
    )
    artifacts = [Path(p) for p in args.artifacts]
    if loaded_bundle is not None:
        artifacts.extend(release_bundle.artifact_paths(loaded_bundle))
    if args.install_state:
        artifacts.append(Path(args.install_state))
    deduped: List[Path] = []
    seen = set()
    for artifact in artifacts:
        key = artifact.as_posix()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(artifact)
    bundle = build_bundle(deduped, bundle=loaded_bundle, install_state=install_state)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    print(f"support-bundle: {out_path}")
    print(f"evidence_items: {len(bundle['evidence'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
