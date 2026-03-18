#!/usr/bin/env python3
"""Helpers for staging default-lane shipping bundles and install state."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import runtime_capture_common_v1 as runtime_capture


SCHEMA = "rugo.release_bundle.v1"
INSTALL_STATE_SCHEMA = "rugo.install_state.v1"
DEFAULT_RELEASE_ROOT = Path("out/releases")
DEFAULT_BUNDLE_PATH = Path("out/release-bundle-v1.json")
DEFAULT_INSTALL_STATE_PATH = Path("out/install-state-v1.json")
DEFAULT_RELEASE_NOTES_LINES = [
    "Current shipping lane: default `image-go` boot path.",
    "Installer and recovery media reuse the shipped default lane ISO.",
    "Known limitations: support claims only cover the default QEMU release lane.",
]
CHANNEL_SUPPORT_DAYS = {
    "nightly": 14,
    "beta": 45,
    "stable": 180,
    "lts": 730,
}


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_file(path: Path) -> str:
    return runtime_capture.sha256_file(path)


def _stable_digest(payload: Dict[str, object]) -> str:
    return runtime_capture.stable_digest(payload)


def version_build(version: str, build_sequence: int) -> str:
    return f"{version}+build.{build_sequence}"


def release_dir(
    *,
    release_root: Path,
    channel: str,
    version: str,
    build_sequence: int,
) -> Path:
    return release_root / channel / version_build(version, build_sequence)


def artifact_by_role(bundle: Dict[str, object], role: str) -> Dict[str, object]:
    for artifact in bundle.get("artifacts", []):
        if isinstance(artifact, dict) and artifact.get("role") == role:
            return artifact
    raise KeyError(f"missing bundle artifact role: {role}")


def artifact_paths(bundle: Dict[str, object], roles: Iterable[str] | None = None) -> List[Path]:
    selected = set(roles or [])
    paths: List[Path] = []
    for artifact in bundle.get("artifacts", []):
        if not isinstance(artifact, dict):
            continue
        role = str(artifact.get("role", ""))
        if selected and role not in selected:
            continue
        path = artifact.get("path")
        if isinstance(path, str) and path:
            paths.append(Path(path))
    notes = bundle.get("release_notes")
    if isinstance(notes, dict):
        path = notes.get("path")
        if isinstance(path, str) and path:
            paths.append(Path(path))
    runtime_info = bundle.get("runtime_capture")
    if isinstance(runtime_info, dict):
        path = runtime_info.get("path")
        if isinstance(path, str) and path:
            paths.append(Path(path))
    return paths


def write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_bundle(path: Path) -> Dict[str, object]:
    payload = read_json(path)
    if payload.get("schema") != SCHEMA:
        raise ValueError(f"unexpected release bundle schema in {path}")
    return payload


def load_install_state(path: Path) -> Dict[str, object]:
    payload = read_json(path)
    if payload.get("schema") != INSTALL_STATE_SCHEMA:
        raise ValueError(f"unexpected install state schema in {path}")
    return payload


def _copy_artifact(src: Path, dest: Path) -> Dict[str, object]:
    if not src.is_file():
        raise FileNotFoundError(f"artifact not found: {src}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
    return {
        "path": dest.as_posix(),
        "source_path": src.as_posix(),
        "sha256": _sha256_file(dest),
        "size": dest.stat().st_size,
    }


def _notes_text(
    *,
    channel: str,
    version: str,
    build_sequence: int,
    artifacts: Sequence[Dict[str, object]],
    capture_mode: str,
    release_notes_lines: Sequence[str] | None,
) -> str:
    lines = [
        f"# Rugo {version_build(version, build_sequence)}",
        "",
        f"- Channel: `{channel}`",
        f"- Build sequence: `{build_sequence}`",
        "- Source lane: `image-go`",
        f"- Runtime capture mode: `{capture_mode}`",
        "",
        "## Bootable artifacts",
        "",
    ]
    for artifact in artifacts:
        if artifact.get("bootable") is not True:
            continue
        lines.append(
            f"- `{artifact['role']}`: `{artifact['path']}` sha256=`{artifact['sha256']}`"
        )
    lines.extend(["", "## Notes", ""])
    for note in release_notes_lines or DEFAULT_RELEASE_NOTES_LINES:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def _stage_runtime_capture(
    *,
    system_image_path: Path,
    kernel_path: Path,
    panic_image_path: Path,
    capture_mode: str,
) -> Dict[str, object]:
    if capture_mode == "auto":
        if runtime_capture.qemu_available():
            try:
                return runtime_capture.collect_booted_runtime(
                    image_path=system_image_path.as_posix(),
                    kernel_path=kernel_path.as_posix(),
                    panic_image_path=panic_image_path.as_posix(),
                )
            except (RuntimeError, TimeoutError, FileNotFoundError):
                pass
        capture_mode = "fixture"
    if capture_mode == "booted_qemu":
        return runtime_capture.collect_booted_runtime(
            image_path=system_image_path.as_posix(),
            kernel_path=kernel_path.as_posix(),
            panic_image_path=panic_image_path.as_posix(),
        )
    if capture_mode == "fixture":
        return runtime_capture.build_fixture_capture(
            image_path=system_image_path.as_posix(),
            kernel_path=kernel_path.as_posix(),
            panic_image_path=panic_image_path.as_posix(),
        )
    raise ValueError(f"unsupported capture mode: {capture_mode}")


def stage_release_bundle(
    *,
    channel: str,
    version: str,
    build_sequence: int,
    system_image: Path,
    kernel: Path,
    panic_image: Path,
    release_root: Path = DEFAULT_RELEASE_ROOT,
    capture_mode: str = "auto",
    release_notes_lines: Sequence[str] | None = None,
) -> Dict[str, object]:
    if build_sequence <= 0:
        raise ValueError("build_sequence must be > 0")

    bundle_dir = release_dir(
        release_root=release_root,
        channel=channel,
        version=version,
        build_sequence=build_sequence,
    )
    bundle_dir.mkdir(parents=True, exist_ok=True)
    tag = version_build(version, build_sequence)

    staged: List[Dict[str, object]] = []
    for role, source, suffix, bootable, description in [
        (
            "system_image",
            system_image,
            "system.iso",
            True,
            "versioned default-lane system image",
        ),
        (
            "installer_image",
            system_image,
            "installer.iso",
            True,
            "operator-facing installer media backed by the default lane image",
        ),
        (
            "recovery_image",
            system_image,
            "recovery.iso",
            True,
            "operator-facing recovery media backed by the default lane image",
        ),
        (
            "kernel",
            kernel,
            "kernel.elf",
            False,
            "kernel artifact paired with the shipped system image",
        ),
        (
            "panic_image",
            panic_image,
            "panic.iso",
            True,
            "panic/recovery validation image for provenance-linked diagnostics",
        ),
    ]:
        staged_path = bundle_dir / f"rugo-{tag}-{channel}-{suffix}"
        artifact = _copy_artifact(source, staged_path)
        artifact["role"] = role
        artifact["bootable"] = bootable
        artifact["description"] = description
        staged.append(artifact)

    system_artifact = artifact_by_role({"artifacts": staged}, "system_image")
    kernel_artifact = artifact_by_role({"artifacts": staged}, "kernel")
    panic_artifact = artifact_by_role({"artifacts": staged}, "panic_image")
    capture = _stage_runtime_capture(
        system_image_path=Path(system_artifact["path"]),
        kernel_path=Path(kernel_artifact["path"]),
        panic_image_path=Path(panic_artifact["path"]),
        capture_mode=capture_mode,
    )
    runtime_capture_path = bundle_dir / "booted-runtime-v1.json"
    write_json(runtime_capture_path, capture)
    runtime_capture_digest = _sha256_file(runtime_capture_path)

    capture_mode_resolved = str(capture.get("capture_mode", capture_mode))
    release_notes_path = bundle_dir / "release-notes.md"
    release_notes_path.write_text(
        _notes_text(
            channel=channel,
            version=version,
            build_sequence=build_sequence,
            artifacts=staged,
            capture_mode=capture_mode_resolved,
            release_notes_lines=release_notes_lines,
        ),
        encoding="utf-8",
    )

    bundle = {
        "schema": SCHEMA,
        "created_utc": _now_utc(),
        "selected_channel": channel,
        "version": version,
        "build_sequence": build_sequence,
        "version_build": tag,
        "release_dir": bundle_dir.as_posix(),
        "source_lane": "image-go",
        "execution_lane": "default-go",
        "support_days": CHANNEL_SUPPORT_DAYS.get(channel, 0),
        "artifacts": staged,
        "runtime_capture": {
            "path": runtime_capture_path.as_posix(),
            "sha256": runtime_capture_digest,
            "capture_id": capture.get("capture_id", ""),
            "trace_id": capture.get("trace_id", ""),
            "build_id": capture.get("build_id", ""),
            "capture_mode": capture_mode_resolved,
            "boot_profiles": capture.get("boot_profiles", []),
        },
        "release_notes": {
            "path": release_notes_path.as_posix(),
            "sha256": _sha256_file(release_notes_path),
        },
        "reproducibility_inputs": {
            "system_image_source": system_image.as_posix(),
            "system_image_source_sha256": _sha256_file(system_image),
            "kernel_source": kernel.as_posix(),
            "kernel_source_sha256": _sha256_file(kernel),
            "panic_image_source": panic_image.as_posix(),
            "panic_image_source_sha256": _sha256_file(panic_image),
        },
        "update_repo_targets": [
            artifact["path"]
            for artifact in staged
            if artifact["role"] in {"system_image", "installer_image", "recovery_image"}
        ],
    }
    bundle["digest"] = _stable_digest(
        {key: value for key, value in bundle.items() if key != "digest"}
    )
    return bundle


def build_install_state(
    *,
    bundle: Dict[str, object],
    bundle_path: str = "",
    installed_version: str | None = None,
    installed_build_sequence: int | None = None,
    bootstrap_slot: str = "A",
    candidate_slot: str = "B",
) -> Dict[str, object]:
    if bootstrap_slot == candidate_slot:
        raise ValueError("bootstrap and candidate slots must differ")

    system_artifact = artifact_by_role(bundle, "system_image")
    recovery_artifact = artifact_by_role(bundle, "recovery_image")
    installer_artifact = artifact_by_role(bundle, "installer_image")

    candidate_build = int(bundle["build_sequence"])
    active_build = (
        installed_build_sequence
        if installed_build_sequence is not None
        else max(1, candidate_build - 1)
    )
    active_version = installed_version or str(bundle["version"])

    slots = [
        {
            "name": bootstrap_slot,
            "role": "active",
            "version": active_version,
            "build_sequence": active_build,
            "artifact_path": system_artifact["path"],
            "artifact_sha256": system_artifact["sha256"],
            "trusted": True,
        },
        {
            "name": candidate_slot,
            "role": "standby",
            "version": bundle["version"],
            "build_sequence": candidate_build,
            "artifact_path": installer_artifact["path"],
            "artifact_sha256": installer_artifact["sha256"],
            "trusted": True,
        },
    ]
    return {
        "schema": INSTALL_STATE_SCHEMA,
        "created_utc": _now_utc(),
        "selected_channel": bundle["selected_channel"],
        "release_bundle_digest": bundle["digest"],
        "release_bundle_path": bundle_path or DEFAULT_BUNDLE_PATH.as_posix(),
        "active_slot": bootstrap_slot,
        "candidate_slot": candidate_slot,
        "last_trusted_slot": bootstrap_slot,
        "trusted_floor_sequence": active_build,
        "recovery_media": {
            "path": recovery_artifact["path"],
            "sha256": recovery_artifact["sha256"],
        },
        "runtime_capture": dict(bundle.get("runtime_capture", {})),
        "slots": slots,
        "history": [
            {
                "event": "install_seeded",
                "slot": bootstrap_slot,
                "version": active_version,
                "build_sequence": active_build,
            }
        ],
    }


def write_install_state(path: Path, payload: Dict[str, object]) -> None:
    write_json(path, payload)
