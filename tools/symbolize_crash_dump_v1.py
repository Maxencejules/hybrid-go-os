#!/usr/bin/env python3
"""Symbolize a crash dump artifact using deterministic symbol mapping."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


SYMBOLS = {
    "0xffffffff80001000": "kernel::panic_entry",
    "0xffffffff80002000": "kernel::scheduler::tick",
    "0xffffffff80003000": "kernel::syscall::dispatch",
}


def symbolize(dump: Dict[str, object]) -> Dict[str, object]:
    frames = []
    for frame in dump.get("stack_frames", []):
        ip = str(frame.get("ip"))
        frames.append(
            {
                "ip": ip,
                "symbol": SYMBOLS.get(ip, "unknown"),
                "offset": frame.get("offset", 0),
            }
        )
    return {
        "schema": "rugo.crash_dump_symbolized.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_schema": dump.get("schema", "unknown"),
        "panic_code": dump.get("panic_code", -1),
        "frames": frames,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dump", default="")
    p.add_argument("--out", default="out/crash-dump-symbolized-v1.json")
    return p


def _default_dump() -> Dict[str, object]:
    return {
        "schema": "rugo.crash_dump.v1",
        "panic_code": 13,
        "stack_frames": [
            {"ip": "0xffffffff80001000", "offset": 0},
            {"ip": "0xffffffff80002000", "offset": 24},
            {"ip": "0xffffffff80003000", "offset": 56},
        ],
    }


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.dump:
        dump = json.loads(Path(args.dump).read_text(encoding="utf-8"))
    else:
        dump = _default_dump()
    report = symbolize(dump)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"crash-dump-symbolized: {out_path}")
    print(f"frames: {len(report['frames'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

