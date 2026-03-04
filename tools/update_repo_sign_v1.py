#!/usr/bin/env python3
"""Sign update repository metadata for M14."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


SCHEMA = "rugo.update_metadata.v1"
SIG_ALG = "hmac-sha256"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sign_payload(payload: Dict[str, Any], key: str) -> str:
    return hmac.new(key.encode("utf-8"), _canonical_json(payload), hashlib.sha256).hexdigest()


def _bootstrap_targets(repo: Path, version: str) -> None:
    targets_dir = repo / "targets"
    targets_dir.mkdir(parents=True, exist_ok=True)
    if any(p.is_file() for p in targets_dir.rglob("*")):
        return

    target = targets_dir / f"system-image-{version}.bin"
    payload = f"rugo release image {version}\n".encode("utf-8")
    target.write_bytes(payload)


def _collect_targets(repo: Path) -> List[Dict[str, object]]:
    targets_dir = repo / "targets"
    files = sorted([p for p in targets_dir.rglob("*") if p.is_file()])
    out: List[Dict[str, object]] = []
    for path in files:
        rel = path.relative_to(repo).as_posix()
        out.append(
            {
                "path": rel,
                "sha256": _sha256_file(path),
                "size": path.stat().st_size,
            }
        )
    return out


def build_signed_metadata(
    repo: Path,
    channel: str,
    version: str,
    build_sequence: int,
    key: str,
    key_id: str,
    expires_hours: int,
) -> Dict[str, Any]:
    if build_sequence <= 0:
        raise ValueError("build_sequence must be > 0")

    _bootstrap_targets(repo, version=version)
    targets = _collect_targets(repo)
    if not targets:
        raise ValueError("no targets found in repository")

    created = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "schema": SCHEMA,
        "channel": channel,
        "version": version,
        "build_sequence": build_sequence,
        "rollback_floor_sequence": build_sequence,
        "created_utc": created.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "expires_utc": (created + timedelta(hours=expires_hours)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "targets": targets,
    }
    signature = {
        "key_id": key_id,
        "alg": SIG_ALG,
        "value": _sign_payload(payload, key),
    }
    out = dict(payload)
    out["signature"] = signature
    return out


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", default="out/update-repo-v1")
    p.add_argument("--channel", default="stable")
    p.add_argument("--version", default="1.0.0")
    p.add_argument("--build-sequence", type=int, default=1)
    p.add_argument("--expires-hours", type=int, default=168)
    p.add_argument("--key", default="m14-update-key-v1")
    p.add_argument("--key-id", default="update-key-2026-03")
    p.add_argument("--out", default="out/update-metadata-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    repo = Path(args.repo)
    repo.mkdir(parents=True, exist_ok=True)

    metadata = build_signed_metadata(
        repo=repo,
        channel=args.channel,
        version=args.version,
        build_sequence=args.build_sequence,
        key=args.key,
        key_id=args.key_id,
        expires_hours=args.expires_hours,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    repo_meta = repo / "metadata" / "update-metadata-v1.json"
    repo_meta.parent.mkdir(parents=True, exist_ok=True)
    repo_meta.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print(f"update-metadata: {out_path}")
    print(f"repo-metadata: {repo_meta}")
    print(f"build_sequence: {metadata['build_sequence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
