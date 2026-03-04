#!/usr/bin/env python3
"""M10 secure-boot manifest v1: sign and verify boot artifacts."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SCHEMA = "rugo.secure_boot_manifest.v1"
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
    msg = _canonical_json(payload)
    return hmac.new(key.encode("utf-8"), msg, hashlib.sha256).hexdigest()


def _manifest_payload(
    artifacts: List[Dict[str, Any]],
    key_id: str,
    created_utc: str | None = None,
) -> Dict[str, Any]:
    return {
        "schema": SCHEMA,
        "key_id": key_id,
        "created_utc": created_utc
        if created_utc is not None
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "artifacts": artifacts,
    }


def sign_manifest(
    artifact_paths: List[Path],
    key: str,
    key_id: str,
    base_dir: Path | None = None,
) -> Dict[str, Any]:
    base = Path.cwd() if base_dir is None else base_dir
    artifacts: List[Dict[str, Any]] = []
    for path in artifact_paths:
        p = path if path.is_absolute() else (base / path)
        if not p.is_file():
            raise FileNotFoundError(f"artifact not found: {p}")
        rel = os.path.relpath(p, base)
        artifacts.append(
            {
                "path": rel.replace("\\", "/"),
                "sha256": _sha256_file(p),
                "size": p.stat().st_size,
            }
        )
    payload = _manifest_payload(artifacts=artifacts, key_id=key_id)
    sig = _sign_payload(payload, key)
    out = dict(payload)
    out["signature"] = {"alg": SIG_ALG, "value": sig}
    return out


def verify_manifest(
    manifest: Dict[str, Any],
    key: str,
    base_dir: Path | None = None,
) -> bool:
    base = Path.cwd() if base_dir is None else base_dir

    if manifest.get("schema") != SCHEMA:
        return False

    sig = manifest.get("signature", {})
    if sig.get("alg") != SIG_ALG:
        return False
    sig_value = sig.get("value")
    if not isinstance(sig_value, str) or len(sig_value) != 64:
        return False

    payload = {
        "schema": manifest.get("schema"),
        "key_id": manifest.get("key_id"),
        "created_utc": manifest.get("created_utc"),
        "artifacts": manifest.get("artifacts"),
    }
    expected_sig = _sign_payload(payload, key)
    if not hmac.compare_digest(expected_sig, sig_value):
        return False

    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) == 0:
        return False

    for art in artifacts:
        if not isinstance(art, dict):
            return False
        rel_path = art.get("path")
        expected_hash = art.get("sha256")
        expected_size = art.get("size")
        if not isinstance(rel_path, str) or not rel_path:
            return False
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            return False
        if not isinstance(expected_size, int) or expected_size < 0:
            return False
        p = (base / rel_path).resolve()
        if not p.is_file():
            return False
        if p.stat().st_size != expected_size:
            return False
        if _sha256_file(p) != expected_hash:
            return False

    return True


def _cmd_sign(args: argparse.Namespace) -> int:
    artifacts = [Path(p) for p in args.artifacts]
    manifest = sign_manifest(
        artifact_paths=artifacts,
        key=args.key,
        key_id=args.key_id,
        base_dir=Path(args.base_dir).resolve(),
    )
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"signed: {out_path}")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).resolve()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    ok = verify_manifest(
        manifest=data,
        key=args.key,
        base_dir=Path(args.base_dir).resolve(),
    )
    print("verify: ok" if ok else "verify: fail")
    return 0 if ok else 1


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sign_p = sub.add_parser("sign", help="sign a secure-boot manifest")
    sign_p.add_argument("--key", required=True, help="HMAC key material")
    sign_p.add_argument("--key-id", required=True, help="signing key identifier")
    sign_p.add_argument("--base-dir", default=".", help="base path for relative artifact paths")
    sign_p.add_argument("--out", required=True, help="manifest output path")
    sign_p.add_argument("--artifacts", nargs="+", required=True, help="artifact file paths")
    sign_p.set_defaults(func=_cmd_sign)

    verify_p = sub.add_parser("verify", help="verify a secure-boot manifest")
    verify_p.add_argument("--key", required=True, help="HMAC key material")
    verify_p.add_argument("--base-dir", default=".", help="base path for relative artifact paths")
    verify_p.add_argument("--manifest", required=True, help="manifest file path")
    verify_p.set_defaults(func=_cmd_verify)

    return p


def main(argv: List[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
