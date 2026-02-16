#!/usr/bin/env python3
"""Build a SimpleFS disk image with hello.pkg pre-written."""
import struct
import sys


def build_disk(hello_bin_path, output_path):
    with open(hello_bin_path, "rb") as f:
        hello_bin = f.read()

    # Build hello.pkg: 32-byte header + binary
    name_bytes = b"hello\x00" + b"\x00" * 18  # padded to 24 bytes
    pkg_header = struct.pack("<II24s", 0x01474B50, len(hello_bin), name_bytes)
    hello_pkg = pkg_header + hello_bin

    # Layout: sector 0 = superblock, sector 1 = file table, sectors 2+ = data
    data_start = 2
    pkg_sectors = (len(hello_pkg) + 511) // 512
    next_free = data_start + pkg_sectors

    # Superblock (sector 0)
    superblock = struct.pack("<IIII", 0x53465331, 1, data_start, next_free)
    superblock = superblock.ljust(512, b"\x00")

    # File table (sector 1): one entry for "hello.pkg"
    entry_name = b"hello.pkg\x00" + b"\x00" * 14  # padded to 24 bytes
    entry = struct.pack("<24sII", entry_name, data_start, len(hello_pkg))
    file_table = entry.ljust(512, b"\x00")

    # Data sectors
    data = hello_pkg.ljust(pkg_sectors * 512, b"\x00")

    # Assemble full disk (1 MB)
    disk = superblock + file_table + data
    disk = disk.ljust(1024 * 1024, b"\x00")

    with open(output_path, "wb") as f:
        f.write(disk)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <hello.bin> <output.img>", file=sys.stderr)
        sys.exit(1)
    build_disk(sys.argv[1], sys.argv[2])
