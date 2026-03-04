#!/usr/bin/env python3
"""Run deterministic storage recovery/integrity checks for M13."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


SFS_MAGIC = 0x53465331


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def analyze_image_bytes(image: bytes) -> Dict[str, object]:
    checks: Dict[str, bool] = {
        "has_min_superblock": len(image) >= 16,
    }
    if checks["has_min_superblock"]:
        magic = int.from_bytes(image[0:4], "little")
        file_count = int.from_bytes(image[4:8], "little")
        data_start = int.from_bytes(image[8:12], "little")
        next_free = int.from_bytes(image[12:16], "little")
    else:
        magic = 0
        file_count = 0
        data_start = 0
        next_free = 0

    checks["magic_ok"] = magic == SFS_MAGIC
    checks["file_count_ok"] = file_count <= 16
    checks["data_start_ok"] = data_start >= 2
    checks["next_free_ok"] = next_free >= data_start

    mountable = all(checks.values())
    total_issues = sum(1 for ok in checks.values() if not ok)

    return {
        "checks": checks,
        "mountable": mountable,
        "total_issues": total_issues,
        "superblock": {
            "magic_le": magic,
            "file_count": file_count,
            "data_start": data_start,
            "next_free": next_free,
        },
    }


def build_report(image_path: Path, check_mode: bool) -> Dict[str, object]:
    if not image_path.is_file():
        return {
            "schema": "rugo.storage_recovery_report.v1",
            "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "mode": "check" if check_mode else "report",
            "image": str(image_path),
            "image_present": False,
            "checks": {"image_present": False},
            "mountable": False,
            "total_issues": 1,
        }

    data = image_path.read_bytes()
    analysis = analyze_image_bytes(data)
    return {
        "schema": "rugo.storage_recovery_report.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": "check" if check_mode else "report",
        "image": str(image_path),
        "image_present": True,
        "image_size_bytes": len(data),
        "image_sha256": sha256_bytes(data),
        "checks": analysis["checks"],
        "mountable": analysis["mountable"],
        "total_issues": analysis["total_issues"],
        "superblock": analysis["superblock"],
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true", help="enforce mountable report")
    p.add_argument("--image", default="out/fs-test.img")
    p.add_argument("--out", default="out/storage-recovery-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    image_path = Path(args.image)
    out_path = Path(args.out)

    report = build_report(image_path=image_path, check_mode=args.check)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"storage-recovery-report: {out_path}")
    print(f"mountable: {report['mountable']}")
    if args.check and not bool(report["mountable"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
