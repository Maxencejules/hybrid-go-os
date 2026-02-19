#!/usr/bin/env python3
"""Build a SimpleFS v0 disk image with hello.pkg for M6 tests.

On-disk layout (see docs/storage/fs_v0.md):
  Sector 0: Superblock (magic, file_count, data_start, next_free)
  Sector 1: File table (16 entries x 32 bytes)
  Sector 2+: Data sectors

Package format v0 (hello.pkg):
  Offset 0:  magic     (u32le) = 0x01474B50 ("PKG\\x01")
  Offset 4:  bin_size  (u32le) = size of binary payload
  Offset 8:  name      (24 bytes, NUL-padded)
  Offset 32: binary payload
"""

import os
import struct
import sys

# SimpleFS magic: "SFS1" as little-endian u32
SFS_MAGIC = 0x53465331

# Package magic: "PKG\\x01" as little-endian u32
PKG_MAGIC = 0x01474B50

# Hello binary — x86-64 user-mode code that prints "APP: hello world\n"
# and then HLTs (triggering GPF -> kernel exit).
#
# Assembly:
#   lea rdi, [rip+12]        ; pointer to message string
#   mov rsi, 17              ; length
#   xor eax, eax             ; syscall 0 = sys_debug_write
#   int 0x80
#   hlt                      ; GPF in ring 3 -> clean exit
#   .msg: "APP: hello world\n"
HELLO_BINARY = bytes([
    0x48, 0x8D, 0x3D, 0x0C, 0x00, 0x00, 0x00,  # lea rdi, [rip+12]
    0x48, 0xC7, 0xC6, 0x11, 0x00, 0x00, 0x00,  # mov rsi, 17
    0x31, 0xC0,                                  # xor eax, eax
    0xCD, 0x80,                                  # int 0x80
    0xF4,                                        # hlt
    # "APP: hello world\n" (17 bytes)
    0x41, 0x50, 0x50, 0x3A, 0x20,               # "APP: "
    0x68, 0x65, 0x6C, 0x6C, 0x6F, 0x20,         # "hello "
    0x77, 0x6F, 0x72, 0x6C, 0x64, 0x0A,         # "world\n"
])


def build_pkg(name, binary):
    """Build a PKG v0 package: 32-byte header + binary payload."""
    header = struct.pack('<II', PKG_MAGIC, len(binary))
    name_bytes = name.encode('ascii')[:24].ljust(24, b'\x00')
    header += name_bytes
    assert len(header) == 32
    return header + binary


def build_disk_image(output_path, corrupt_superblock_magic=False):
    """Create a 1 MiB SimpleFS v0 disk image."""
    disk_size = 1024 * 1024  # 1 MiB
    disk = bytearray(disk_size)

    # Build hello.pkg
    hello_pkg = build_pkg("hello", HELLO_BINARY)

    # Layout: sector 0 = superblock, sector 1 = file table, sector 2+ = data
    file_count = 1
    data_start = 2
    pkg_sectors = (len(hello_pkg) + 511) // 512
    next_free = data_start + pkg_sectors

    # Superblock -> sector 0
    sb_magic = 0 if corrupt_superblock_magic else SFS_MAGIC
    sb = struct.pack('<IIII', sb_magic, file_count, data_start, next_free)
    disk[0:len(sb)] = sb

    # File table -> sector 1
    # Entry: name(24) + start_sector(u32le) + size_bytes(u32le) = 32 bytes
    entry_name = b'hello.pkg\x00' + b'\x00' * 14  # 24 bytes padded
    entry = entry_name + struct.pack('<II', data_start, len(hello_pkg))
    assert len(entry) == 32
    disk[512:512 + len(entry)] = entry

    # Data -> sector 2+
    data_offset = data_start * 512
    disk[data_offset:data_offset + len(hello_pkg)] = hello_pkg

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(disk)

    print(f"==> FS disk image ready: {output_path}")
    print(f"    SimpleFS: {file_count} file(s), data_start={data_start}, "
          f"next_free={next_free}")
    print(f"    hello.pkg: {len(hello_pkg)} bytes "
          f"(header=32, binary={len(HELLO_BINARY)})")


if __name__ == '__main__':
    output = 'out/fs-test.img'
    corrupt_superblock_magic = False
    for arg in sys.argv[1:]:
        if arg == '--corrupt-superblock-magic':
            corrupt_superblock_magic = True
        elif output == 'out/fs-test.img':
            output = arg
        else:
            raise SystemExit(
                'Usage: mkfs.py [output_path] [--corrupt-superblock-magic]'
            )
    build_disk_image(output, corrupt_superblock_magic=corrupt_superblock_magic)
