#!/usr/bin/env python3
"""Stage a versioned shipping bundle for the default bootable image lane."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import release_bundle_v1 as bundle_tool


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", default="stable")
    parser.add_argument("--version", default="1.0.0")
    parser.add_argument("--build-sequence", type=int, default=1)
    parser.add_argument("--system-image", default="out/os-go.iso")
    parser.add_argument("--kernel", default="out/kernel-go.elf")
    parser.add_argument("--panic-image", default="out/os-panic.iso")
    parser.add_argument("--release-root", default=str(bundle_tool.DEFAULT_RELEASE_ROOT))
    parser.add_argument(
        "--capture-mode",
        choices=["auto", "fixture", "booted_qemu"],
        default="auto",
    )
    parser.add_argument(
        "--release-note",
        action="append",
        default=[],
        help="append a release note bullet to the generated release notes",
    )
    parser.add_argument("--out", default=str(bundle_tool.DEFAULT_BUNDLE_PATH))
    return parser


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.build_sequence <= 0:
        print("error: --build-sequence must be > 0")
        return 2

    try:
        bundle = bundle_tool.stage_release_bundle(
            channel=args.channel,
            version=args.version,
            build_sequence=args.build_sequence,
            system_image=Path(args.system_image),
            kernel=Path(args.kernel),
            panic_image=Path(args.panic_image),
            release_root=Path(args.release_root),
            capture_mode=args.capture_mode,
            release_notes_lines=args.release_note or None,
        )
    except (FileNotFoundError, RuntimeError, TimeoutError, ValueError) as exc:
        print(f"error: {exc}")
        return 1

    out_path = Path(args.out)
    bundle_tool.write_json(out_path, bundle)
    print(f"release-bundle: {out_path}")
    print(f"release-dir: {bundle['release_dir']}")
    print(f"capture-mode: {bundle['runtime_capture']['capture_mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
