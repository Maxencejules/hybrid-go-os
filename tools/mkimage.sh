#!/usr/bin/env bash
# Build a bootable ISO: Limine BIOS + kernel ELF.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/out"
ISO_ROOT="$OUT/iso_root"
LIMINE_DIR="$ROOT/limine"
LIMINE_BRANCH="${LIMINE_BRANCH:-v8.x-binary}"

# --- Fetch Limine if needed ---------------------------------------------------
if [ ! -f "$LIMINE_DIR/limine" ]; then
    echo "==> Fetching Limine ($LIMINE_BRANCH)..."
    rm -rf "$LIMINE_DIR"
    git clone https://github.com/limine-bootloader/limine.git \
        --branch="$LIMINE_BRANCH" --depth=1 "$LIMINE_DIR"
    make -C "$LIMINE_DIR"
fi

# --- Assemble ISO tree --------------------------------------------------------
rm -rf "$ISO_ROOT"
mkdir -p "$ISO_ROOT/boot/limine"

cp "$OUT/kernel.elf"                 "$ISO_ROOT/boot/kernel.elf"
cp "$ROOT/boot/limine.conf"         "$ISO_ROOT/boot/limine/limine.conf"
cp "$LIMINE_DIR/limine-bios.sys"    "$ISO_ROOT/boot/limine/"
cp "$LIMINE_DIR/limine-bios-cd.bin" "$ISO_ROOT/boot/limine/"

# --- Create ISO ---------------------------------------------------------------
xorriso -as mkisofs \
    -R -r -J \
    -b boot/limine/limine-bios-cd.bin \
    -no-emul-boot -boot-load-size 4 -boot-info-table \
    -o "$OUT/os.iso" \
    "$ISO_ROOT"

# --- Install Limine BIOS boot stages -----------------------------------------
"$LIMINE_DIR/limine" bios-install "$OUT/os.iso"

echo "==> Image ready: $OUT/os.iso"
