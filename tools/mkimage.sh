#!/usr/bin/env bash
# Build a bootable ISO: Limine BIOS + kernel ELF.
# Limine binaries and CLI source are vendored in vendor/limine/.
# No network access is required.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/out"
ISO_ROOT="$OUT/iso_root"
VENDOR_LIMINE="$ROOT/vendor/limine"

# Callers can override which kernel ELF and output ISO name to use.
KERNEL_ELF="${KERNEL_ELF:-kernel.elf}"
ISO_NAME="${ISO_NAME:-os.iso}"

# --- Build Limine CLI from vendored source (if needed) ------------------------
LIMINE_CLI="$OUT/limine-cli"
if [ ! -f "$LIMINE_CLI" ]; then
    echo "==> Building Limine CLI from vendored source..."
    mkdir -p "$OUT"
    cc -O2 -pipe -Wall -Wextra -std=c99 \
        -o "$LIMINE_CLI" "$VENDOR_LIMINE/limine.c"
fi

# --- Assemble ISO tree --------------------------------------------------------
rm -rf "$ISO_ROOT"
mkdir -p "$ISO_ROOT/boot/limine"

cp "$OUT/$KERNEL_ELF"                       "$ISO_ROOT/boot/kernel.elf"
cp "$ROOT/boot/limine.conf"                "$ISO_ROOT/boot/limine/limine.conf"
cp "$VENDOR_LIMINE/limine-bios.sys"        "$ISO_ROOT/boot/limine/"
cp "$VENDOR_LIMINE/limine-bios-cd.bin"     "$ISO_ROOT/boot/limine/"

# --- Create ISO ---------------------------------------------------------------
xorriso -as mkisofs \
    -R -r -J \
    -b boot/limine/limine-bios-cd.bin \
    -no-emul-boot -boot-load-size 4 -boot-info-table \
    -o "$OUT/$ISO_NAME" \
    "$ISO_ROOT"

# --- Install Limine BIOS boot stages -----------------------------------------
"$LIMINE_CLI" bios-install "$OUT/$ISO_NAME"

echo "==> Image ready: $OUT/$ISO_NAME"
