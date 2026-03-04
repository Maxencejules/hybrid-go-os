"""M10 acceptance: secure-boot manifest signing and verification."""

import json
from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2] / "tools"))
import secure_boot_manifest_v1 as sb  # noqa: E402


def _write_file(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def test_manifest_verify_roundtrip(tmp_path: Path):
    art1 = _write_file(tmp_path / "out" / "kernel.elf", b"kernel-v1")
    art2 = _write_file(tmp_path / "out" / "os.iso", b"iso-v1")

    manifest = sb.sign_manifest(
        artifact_paths=[art1, art2],
        key="key-v1",
        key_id="key-2026-03",
        base_dir=tmp_path,
    )

    assert manifest["schema"] == sb.SCHEMA
    assert manifest["key_id"] == "key-2026-03"
    assert sb.verify_manifest(manifest, key="key-v1", base_dir=tmp_path) is True


def test_manifest_rejects_tampered_artifact(tmp_path: Path):
    art = _write_file(tmp_path / "out" / "kernel.elf", b"kernel-v1")
    manifest = sb.sign_manifest(
        artifact_paths=[art],
        key="key-v1",
        key_id="key-2026-03",
        base_dir=tmp_path,
    )

    art.write_bytes(b"kernel-v1-tampered")
    assert sb.verify_manifest(manifest, key="key-v1", base_dir=tmp_path) is False


def test_manifest_key_rotation_path(tmp_path: Path):
    art = _write_file(tmp_path / "out" / "kernel.elf", b"kernel-v1")

    manifest_old = sb.sign_manifest(
        artifact_paths=[art],
        key="key-old",
        key_id="key-2026-03",
        base_dir=tmp_path,
    )
    assert sb.verify_manifest(manifest_old, key="key-old", base_dir=tmp_path) is True
    assert sb.verify_manifest(manifest_old, key="key-new", base_dir=tmp_path) is False

    manifest_new = sb.sign_manifest(
        artifact_paths=[art],
        key="key-new",
        key_id="key-2026-04",
        base_dir=tmp_path,
    )
    assert manifest_new["key_id"] == "key-2026-04"
    assert sb.verify_manifest(manifest_new, key="key-new", base_dir=tmp_path) is True


def test_manifest_cli_sign_verify(tmp_path: Path):
    art = _write_file(tmp_path / "out" / "os.iso", b"iso-v1")
    out_manifest = tmp_path / "out" / "boot-manifest.json"

    rc_sign = sb.main(
        [
            "sign",
            "--key",
            "cli-key",
            "--key-id",
            "cli-key-1",
            "--base-dir",
            str(tmp_path),
            "--out",
            str(out_manifest),
            "--artifacts",
            str(art),
        ]
    )
    assert rc_sign == 0
    assert out_manifest.is_file()
    manifest = json.loads(out_manifest.read_text(encoding="utf-8"))
    assert manifest["signature"]["alg"] == sb.SIG_ALG

    rc_verify = sb.main(
        [
            "verify",
            "--key",
            "cli-key",
            "--base-dir",
            str(tmp_path),
            "--manifest",
            str(out_manifest),
        ]
    )
    assert rc_verify == 0

    rc_bad = sb.main(
        [
            "verify",
            "--key",
            "wrong-key",
            "--base-dir",
            str(tmp_path),
            "--manifest",
            str(out_manifest),
        ]
    )
    assert rc_bad == 1
