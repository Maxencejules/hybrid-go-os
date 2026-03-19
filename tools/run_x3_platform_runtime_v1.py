#!/usr/bin/env python3
"""Generate the shared X3 platform and ecosystem runtime-backed report."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import runtime_capture_common_v1 as runtime_capture
import x3_platform_runtime_common_v1 as x3_runtime


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=x3_runtime.DEFAULT_SEED)
    parser.add_argument(
        "--runtime-capture",
        default=str(x3_runtime.DEFAULT_RUNTIME_CAPTURE_PATH),
        help="existing booted runtime capture; falls back to fixture when missing",
    )
    parser.add_argument(
        "--fixture",
        action="store_true",
        help="force the built-in fixture instead of loading an on-disk runtime capture",
    )
    parser.add_argument(
        "--inject-failure",
        action="append",
        default=[],
        help="force an X3 runtime check to fail by check_id",
    )
    parser.add_argument(
        "--emit-supporting-reports",
        action="store_true",
        help="write supporting reports into the selected output directory",
    )
    parser.add_argument(
        "--supporting-dir",
        default="out",
        help="directory for emitted supporting reports",
    )
    parser.add_argument("--out", default="out/x3-platform-runtime-v1.json")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        injected_failures = x3_runtime.normalize_failures(args.inject_failure)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    capture = x3_runtime.load_runtime_capture(
        runtime_capture_path=args.runtime_capture,
        fixture=args.fixture,
    )
    reports = x3_runtime.collect_source_reports(seed=args.seed)
    report = x3_runtime.build_report(
        seed=args.seed,
        capture=capture,
        reports=reports,
        injected_failures=injected_failures,
    )

    if args.emit_supporting_reports:
        x3_runtime.write_supporting_reports(reports, base_dir=args.supporting_dir)

    out_path = Path(args.out)
    runtime_capture.write_json(out_path, report)
    print(f"x3-platform-runtime-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    print(f"gate_pass: {report['gate_pass']}")
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
