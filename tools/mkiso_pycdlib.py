#!/usr/bin/env python3
"""Create a bootable ISO image from an assembled ISO root using pycdlib."""

from __future__ import annotations

import argparse
from pathlib import Path

import pycdlib


def _normalize_component(name: str, *, is_file: bool) -> str:
    comp = name.upper()
    if comp in ("", ".", ".."):
        raise ValueError(f"invalid path component: {name!r}")

    # Keep ISO names conservative; Rock Ridge/Joliet preserve original names.
    out = []
    for ch in comp:
        if ("A" <= ch <= "Z") or ("0" <= ch <= "9") or ch == "_":
            out.append(ch)
        else:
            out.append("_")
    comp = "".join(out)

    if is_file:
        return f"{comp[:30]};1"

    return comp[:31]


def _iso_dir_path(rel: Path) -> str:
    parts = [_normalize_component(p, is_file=False) for p in rel.parts]
    return "/" + "/".join(parts)


def _iso_file_path(rel: Path) -> str:
    if not rel.parts:
        raise ValueError("file path cannot be root")
    parts = list(rel.parts)
    iso_parts = [_normalize_component(p, is_file=False) for p in parts[:-1]]
    iso_parts.append(_normalize_component(parts[-1], is_file=True))
    return "/" + "/".join(iso_parts)


def _joliet_path(rel: Path) -> str:
    return "/" + rel.as_posix()


def build_iso(iso_root: Path, out_iso: Path) -> None:
    iso = pycdlib.PyCdlib()
    iso.new(
        interchange_level=3,
        vol_ident="RUGO_OS",
        vol_set_ident="RUGO_OS",
        app_ident_str="RUGO_OS",
        pub_ident_str="RUGO",
        preparer_ident_str="RUGO",
        joliet=3,
        rock_ridge="1.09",
    )

    directories = [p for p in iso_root.rglob("*") if p.is_dir()]
    directories.sort(key=lambda p: (len(p.relative_to(iso_root).parts), p.as_posix()))
    for d in directories:
        rel = d.relative_to(iso_root)
        if not rel.parts:
            continue
        iso.add_directory(
            iso_path=_iso_dir_path(rel),
            rr_name=d.name,
            joliet_path=_joliet_path(rel),
        )

    files = [p for p in iso_root.rglob("*") if p.is_file()]
    files.sort(key=lambda p: p.as_posix())
    for f in files:
        rel = f.relative_to(iso_root)
        iso.add_file(
            str(f),
            iso_path=_iso_file_path(rel),
            rr_name=f.name,
            joliet_path=_joliet_path(rel),
        )

    boot_rel = Path("boot/limine/limine-bios-cd.bin")
    boot_src = iso_root / boot_rel
    if not boot_src.is_file():
        raise FileNotFoundError(f"missing El Torito boot image: {boot_src}")

    iso.add_eltorito(
        bootfile_path=_iso_file_path(boot_rel),
        bootcatfile=_iso_file_path(Path("boot/limine/boot.catalog")),
        rr_bootcatname="boot.catalog",
        joliet_bootcatfile="/boot/limine/boot.catalog",
        boot_load_size=4,
        boot_info_table=True,
        media_name="noemul",
        platform_id=0,
    )

    out_iso.parent.mkdir(parents=True, exist_ok=True)
    iso.write(str(out_iso))
    iso.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iso-root", required=True, type=Path)
    parser.add_argument("--out-iso", required=True, type=Path)
    args = parser.parse_args()

    build_iso(args.iso_root.resolve(), args.out_iso.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
