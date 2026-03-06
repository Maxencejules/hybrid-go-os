#!/usr/bin/env python3
"""Generate deterministic crash dump artifact for postmortem tests."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def build_dump(panic_code: int) -> Dict[str, object]:
    return {
        "schema": "rugo.crash_dump.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "panic_code": panic_code,
        "registers": {
            "rip": "0xffffffff80001000",
            "rsp": "0xffffffff8100ff00",
            "rbp": "0xffffffff8100ff30",
        },
        "stack_frames": [
            {"ip": "0xffffffff80001000", "offset": 0},
            {"ip": "0xffffffff80002000", "offset": 24},
            {"ip": "0xffffffff80003000", "offset": 56},
        ],
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--panic-code", type=int, default=13)
    p.add_argument("--out", default="out/crash-dump-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    dump = build_dump(panic_code=args.panic_code)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(dump, indent=2) + "\n", encoding="utf-8")
    print(f"crash-dump: {out_path}")
    print(f"panic_code: {dump['panic_code']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

