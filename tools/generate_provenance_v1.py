#!/usr/bin/env python3
"""Generate release provenance artifact for M14."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
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


def build_provenance(version: str, artifacts: List[Path]) -> Dict[str, object]:
    subjects = []
    for path in artifacts:
        if not path.is_file():
            continue
        subjects.append(
            {
                "name": path.as_posix(),
                "digest": {"sha256": _sha256_file(path)},
            }
        )

    return {
        "schema": "rugo.provenance.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "build_type": "https://slsa.dev/provenance/v1",
        "version": version,
        "builder": {
            "id": "rugo.make.release-engineering-v1",
            "host_os": platform.system(),
            "host_release": platform.release(),
            "python": platform.python_version(),
        },
        "invocation": {
            "entry_point": "make test-release-engineering-v1",
            "source": {
                "repo": "local",
                "revision": os.getenv("GITHUB_SHA", "unknown"),
            },
        },
        "subjects": subjects,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--version", default="1.0.0")
    p.add_argument(
        "--artifacts",
        nargs="*",
        default=[
            "out/kernel.elf",
            "out/os.iso",
            "out/release-contract-v1.json",
            "out/update-attack-suite-v1.json",
        ],
    )
    p.add_argument("--out", default="out/provenance-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    artifacts = [Path(p) for p in args.artifacts]
    provenance = build_provenance(version=args.version, artifacts=artifacts)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(f"provenance: {out_path}")
    print(f"subjects: {len(provenance['subjects'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
