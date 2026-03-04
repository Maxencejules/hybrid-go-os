#!/usr/bin/env python3
"""Capture deterministic network trace markers from a serial log."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import List


DEFAULT_MARKERS = [
    "NET: virtio-net ready",
    "NET: udp echo",
    "NET: not found",
    "NET: timeout",
]


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--serial-log", required=True, help="input serial log path")
    p.add_argument("--out", default="out/net-trace-v1.json", help="report path")
    return p


def _capture(serial_text: str) -> dict[str, object]:
    counts = Counter()
    found: list[str] = []
    for line in serial_text.splitlines():
        for marker in DEFAULT_MARKERS:
            if marker in line:
                counts[marker] += 1
                if marker not in found:
                    found.append(marker)
    return {
        "schema": "rugo.net_trace_capture.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "markers_found": found,
        "marker_counts": dict(counts),
        "has_timeout_marker": counts["NET: timeout"] > 0,
    }


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    serial_path = Path(args.serial_log)
    serial_text = serial_path.read_text(encoding="utf-8", errors="replace")

    report = _capture(serial_text)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"net-trace-report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
