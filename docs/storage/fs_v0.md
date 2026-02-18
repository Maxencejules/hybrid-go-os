# SimpleFS v0 — On-disk format

## Overview

SimpleFS v0 is a minimal filesystem designed for the M6 milestone. It supports
a fixed directory table, contiguous file extents, and read/write by path. The
filesystem is backed by the VirtIO block driver from M5.

## Architecture choice

**Architecture A — services over IPC.** The R4 IPC infrastructure is proven
(PING/PONG, SHM bulk). For v0, the kernel orchestrates the fsd/pkg/sh logic
directly (reading SimpleFS from the VirtIO block disk, parsing the PKG format,
extracting the hello binary). The hello app runs in genuine user mode (ring 3).

The IPC + service registry framework is ready for full user-space service
migration in a future iteration.

## On-disk layout

All multi-byte values are little-endian.

### Sector 0 — Superblock (16 bytes used)

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 4 | magic | `0x53465331` ("SFS1") |
| 4 | 4 | file_count | Number of files in the file table |
| 8 | 4 | data_start | First data sector number |
| 12 | 4 | next_free | Next free sector for allocation |

### Sector 1 — File table (512 bytes, 16 entries max)

Each entry is 32 bytes:

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 24 | name | NUL-padded filename |
| 24 | 4 | start_sector | First data sector |
| 28 | 4 | size_bytes | File size in bytes |

Maximum 16 entries (16 x 32 = 512 bytes = one sector).

### Sector 2+ — Data

File data is stored contiguously starting at `start_sector`. Files occupy
`ceil(size_bytes / 512)` sectors.

## Mounting assumptions

- The disk is a raw 1 MiB image attached as a VirtIO block device.
- The kernel validates the superblock magic before printing `FSD: mount ok`.
- The file table is read from sector 1 immediately after mounting.
- There is no journaling, no free-space bitmap, and no subdirectories.

## Package format v0

Packages are stored as regular files in SimpleFS (e.g., `hello.pkg`).

### Header (32 bytes)

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 4 | magic | `0x01474B50` ("PKG\x01") |
| 4 | 4 | bin_size | Size of the binary payload in bytes |
| 8 | 24 | name | NUL-padded application name |

### Payload

Raw binary starting at offset 32. This is the executable code loaded into
user-mode memory.

## Package store layout

For v0, the "package store" is the SimpleFS itself. `pkg` reads `hello.pkg`
from the filesystem, parses the header, and extracts the binary. `sh` loads
the binary into a user-mode page and transfers control via `iretq`.

## Disk image generation

The disk image is built deterministically by `tools/mkfs.py`:

```bash
python3 tools/mkfs.py out/fs-test.img
```

This creates a 1 MiB raw image with:
- Formatted SimpleFS superblock and file table
- `hello.pkg` containing the hello binary (prints "APP: hello world\n")

The Makefile target `image-fs` runs this automatically before building the ISO.
