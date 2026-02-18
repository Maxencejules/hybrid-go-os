#!/usr/bin/env bash
# Build TinyGo user-space binary for Rugo G1.
# Produces out/gousr.bin (flat binary for kernel embedding).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/out"
SVC="$ROOT/services/go"
mkdir -p "$OUT"

# --- Check prerequisites ---
command -v tinygo >/dev/null 2>&1 || { echo "ERROR: tinygo not found in PATH"; exit 1; }
command -v nasm   >/dev/null 2>&1 || { echo "ERROR: nasm not found in PATH";   exit 1; }
command -v objcopy >/dev/null 2>&1 || { echo "ERROR: objcopy not found in PATH"; exit 1; }

# --- Assemble startup + syscall stubs ---
echo "==> Assembling Go startup stubs..."
nasm -f elf64 -o "$OUT/go_start.o" "$SVC/start.asm"

# --- Generate target JSON with absolute paths ---
# TinyGo ldflags need absolute paths since LLD CWD is unpredictable.
# Use forward slashes which work on both Unix and Windows in LLD.
START_OBJ="$(cygpath -m "$OUT/go_start.o" 2>/dev/null || echo "$OUT/go_start.o")"
LINKER_LD="$(cygpath -m "$SVC/linker.ld" 2>/dev/null || echo "$SVC/linker.ld")"

cat > "$OUT/rugo-target.json" <<ENDJSON
{
	"llvm-target": "x86_64-unknown-none-elf",
	"cpu": "x86-64",
	"features": "+soft-float,-mmx,-sse,-sse2,-avx",
	"build-tags": ["rugo", "linux", "amd64"],
	"goos": "linux",
	"goarch": "amd64",
	"gc": "none",
	"scheduler": "none",
	"linker": "ld.lld",
	"rtlib": "compiler-rt",
	"libc": "picolibc",
	"default-stack-size": 4096,
	"cflags": [
		"-mno-red-zone",
		"-mno-sse",
		"-fno-stack-protector",
		"-fno-exceptions",
		"-fno-unwind-tables",
		"-ffunction-sections",
		"-fdata-sections"
	],
	"ldflags": [
		"--entry=_start",
		"-nostdlib",
		"-T${LINKER_LD}",
		"${START_OBJ}"
	],
	"extra-files": []
}
ENDJSON

# --- Build with TinyGo ---
echo "==> Building Go user binary with TinyGo..."
cd "$SVC"
tinygo build -target="$OUT/rugo-target.json" -no-debug -o "$OUT/gousr.elf" .

# --- Convert to flat binary ---
echo "==> Converting to flat binary..."
objcopy -O binary "$OUT/gousr.elf" "$OUT/gousr.bin"
BIN_SIZE=$(stat -c%s "$OUT/gousr.bin" 2>/dev/null || stat -f%z "$OUT/gousr.bin" 2>/dev/null || wc -c < "$OUT/gousr.bin")
echo "==> Go user binary: $OUT/gousr.bin ($BIN_SIZE bytes)"
