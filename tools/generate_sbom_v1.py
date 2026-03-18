#!/usr/bin/env python3
"""Generate a minimal SPDX JSON SBOM artifact for M14."""

from __future__ import annotations

import argparse
import hashlib
import json
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


def build_sbom(name: str, version: str, artifacts: List[Path]) -> Dict[str, object]:
    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    files: List[Dict[str, object]] = []
    for path in artifacts:
        if not path.is_file():
            continue
        files.append(
            {
                "fileName": path.as_posix(),
                "checksums": [
                    {
                        "algorithm": "SHA256",
                        "checksumValue": _sha256_file(path),
                    }
                ],
                "comment": "release artifact",
            }
        )

    return {
        "spdxVersion": "SPDX-2.3",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"{name}-sbom",
        "documentNamespace": f"https://rugo.local/spdx/{name}/{version}",
        "creationInfo": {
            "created": created,
            "creators": ["Tool: generate_sbom_v1.py"],
        },
        "dataLicense": "CC0-1.0",
        "packages": [
            {
                "name": name,
                "SPDXID": "SPDXRef-Package-rugo",
                "versionInfo": version,
                "downloadLocation": "NOASSERTION",
                "licenseConcluded": "NOASSERTION",
            }
        ],
        "files": files,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--name", default="rugo")
    p.add_argument("--version", default="1.0.0")
    p.add_argument("--release-bundle", default="")
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
    p.add_argument("--out", default="out/sbom-v1.spdx.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    artifacts = [Path(p) for p in args.artifacts]
    if args.release_bundle:
        bundle = release_bundle.load_bundle(Path(args.release_bundle))
        artifacts.extend(release_bundle.artifact_paths(bundle))
    deduped: List[Path] = []
    seen = set()
    for artifact in artifacts:
        key = artifact.as_posix()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(artifact)
    sbom = build_sbom(name=args.name, version=args.version, artifacts=deduped)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(sbom, indent=2) + "\n", encoding="utf-8")
    print(f"sbom: {out_path}")
    print(f"files: {len(sbom['files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
