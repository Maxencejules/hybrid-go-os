#!/usr/bin/env python3
"""Verify signed update metadata and enforce rollback protection for M14."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


SCHEMA = "rugo.update_metadata.v1"
SIG_ALG = "hmac-sha256"
STATE_SCHEMA = "rugo.update_client_state.v1"


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


def _parse_utc(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _state_template() -> Dict[str, Any]:
    return {
        "schema": STATE_SCHEMA,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "channels": {},
    }


def load_state(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return _state_template()
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != STATE_SCHEMA:
        return _state_template()
    if not isinstance(data.get("channels"), dict):
        data["channels"] = {}
    return data


def verify_metadata(
    metadata: Dict[str, Any],
    repo: Path,
    key: str,
    state: Dict[str, Any],
    expect_version: str | None,
    now_utc: datetime | None = None,
) -> Tuple[bool, str]:
    now = datetime.now(timezone.utc) if now_utc is None else now_utc

    if metadata.get("schema") != SCHEMA:
        return False, "bad_schema"

    signature = metadata.get("signature")
    if not isinstance(signature, dict):
        return False, "missing_signature"
    if signature.get("alg") != SIG_ALG:
        return False, "bad_signature_alg"
    sig_value = signature.get("value")
    if not isinstance(sig_value, str) or len(sig_value) != 64:
        return False, "bad_signature_value"

    payload = {
        "schema": metadata.get("schema"),
        "channel": metadata.get("channel"),
        "version": metadata.get("version"),
        "build_sequence": metadata.get("build_sequence"),
        "rollback_floor_sequence": metadata.get("rollback_floor_sequence"),
        "created_utc": metadata.get("created_utc"),
        "expires_utc": metadata.get("expires_utc"),
        "targets": metadata.get("targets"),
    }
    expected_sig = _sign_payload(payload, key)
    if not hmac.compare_digest(expected_sig, sig_value):
        return False, "bad_signature"

    channel = metadata.get("channel")
    version = metadata.get("version")
    build_sequence = metadata.get("build_sequence")
    rollback_floor = metadata.get("rollback_floor_sequence")
    expires_utc = metadata.get("expires_utc")
    targets = metadata.get("targets")

    if not isinstance(channel, str) or not channel:
        return False, "bad_channel"
    if not isinstance(version, str) or not version:
        return False, "bad_version"
    if expect_version is not None and version != expect_version:
        return False, "unexpected_version"
    if not isinstance(build_sequence, int) or build_sequence <= 0:
        return False, "bad_build_sequence"
    if not isinstance(rollback_floor, int) or rollback_floor <= 0:
        return False, "bad_rollback_floor"
    if build_sequence < rollback_floor:
        return False, "sequence_below_rollback_floor"
    if not isinstance(expires_utc, str):
        return False, "bad_expiry"
    if _parse_utc(expires_utc) <= now:
        return False, "expired_metadata"

    if not isinstance(targets, list) or len(targets) == 0:
        return False, "missing_targets"
    for target in targets:
        if not isinstance(target, dict):
            return False, "bad_target_entry"
        path = target.get("path")
        sha256 = target.get("sha256")
        size = target.get("size")
        if not isinstance(path, str) or not path:
            return False, "bad_target_path"
        if not isinstance(sha256, str) or len(sha256) != 64:
            return False, "bad_target_hash"
        if not isinstance(size, int) or size < 0:
            return False, "bad_target_size"
        file_path = repo / path
        if not file_path.is_file():
            return False, "missing_target_file"
        if file_path.stat().st_size != size:
            return False, "target_size_mismatch"
        if _sha256_file(file_path) != sha256:
            return False, "target_hash_mismatch"

    channels = state.get("channels", {})
    last_seen = channels.get(channel, {})
    last_sequence = int(last_seen.get("build_sequence", 0))
    if build_sequence <= last_sequence:
        return False, "rollback_or_replay"

    return True, "ok"


def write_state(
    state: Dict[str, Any], state_path: Path, channel: str, build_sequence: int, version: str
) -> None:
    channels = state.setdefault("channels", {})
    channels[channel] = {
        "build_sequence": build_sequence,
        "version": version,
        "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", default="out/update-repo-v1")
    p.add_argument("--metadata", default="")
    p.add_argument("--key", default="m14-update-key-v1")
    p.add_argument("--state", default="out/update-client-state-v1.json")
    p.add_argument("--expect-version", default="")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    repo = Path(args.repo)
    metadata_path = (
        Path(args.metadata)
        if args.metadata
        else repo / "metadata" / "update-metadata-v1.json"
    )
    state_path = Path(args.state)
    expect_version = args.expect_version if args.expect_version else None

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    state = load_state(state_path)
    ok, reason = verify_metadata(
        metadata=metadata,
        repo=repo,
        key=args.key,
        state=state,
        expect_version=expect_version,
    )
    print(f"verify: {reason}")
    if not ok:
        return 1

    write_state(
        state=state,
        state_path=state_path,
        channel=str(metadata["channel"]),
        build_sequence=int(metadata["build_sequence"]),
        version=str(metadata["version"]),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
