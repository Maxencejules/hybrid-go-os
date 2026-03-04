#!/usr/bin/env python3
"""Collect deterministic support bundle metadata for M14."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def build_bundle(artifacts: List[Path]) -> Dict[str, object]:
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
        "schema": "rugo.support_bundle.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
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
            "out/release-contract-v1.json",
            "out/update-attack-suite-v1.json",
            "out/sbom-v1.spdx.json",
            "out/provenance-v1.json",
        ],
    )
    p.add_argument("--out", default="out/support-bundle-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    bundle = build_bundle([Path(p) for p in args.artifacts])
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    print(f"support-bundle: {out_path}")
    print(f"evidence_items: {len(bundle['evidence'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
