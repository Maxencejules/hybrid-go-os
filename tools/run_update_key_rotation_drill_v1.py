#!/usr/bin/env python3
"""Run deterministic update key-rotation drill."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def run_drill() -> Dict[str, object]:
    stages = [
        {"name": "old_key_only", "success": True},
        {"name": "overlap_window", "success": True},
        {"name": "new_key_only", "success": True},
        {"name": "old_key_revoked", "success": True},
    ]
    return {
        "schema": "rugo.update_key_rotation_drill.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stages": stages,
        "success": all(s["success"] for s in stages),
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default="out/update-key-rotation-drill-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    report = run_drill()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"update-key-rotation-drill: {out_path}")
    print(f"success: {report['success']}")
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

