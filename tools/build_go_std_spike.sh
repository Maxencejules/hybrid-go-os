#!/usr/bin/env bash
# Build G2 spike user-space binary.
# Produces out/gostd.bin and out/gostd-contract.env.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/out"
SVC="$ROOT/services/go_std"
mkdir -p "$OUT"

CONTRACT_GOOS="rugo"
CONTRACT_GOARCH="amd64"
# Temporary bridge for TinyGo target compatibility until a native rugo GOOS port
# is available in the compiler/runtime.
COMPAT_GOOS="${SPIKE_COMPAT_GOOS:-linux}"

WINUSER="${USERNAME:-}"
if [ -z "$WINUSER" ] && [[ "$ROOT" =~ ^/mnt/c/Users/([^/]+)/ ]]; then
    WINUSER="${BASH_REMATCH[1]}"
fi
if [ -d "/mnt/c/Progra~1/Go/bin" ]; then
    PATH="/mnt/c/Progra~1/Go/bin:$PATH"
elif [ -d "/mnt/c/Program Files/Go/bin" ]; then
    PATH="/mnt/c/Program Files/Go/bin:$PATH"
fi
if [ -n "$WINUSER" ]; then
    TINYGO_WIN_BIN="/mnt/c/Users/$WINUSER/AppData/Local/Microsoft/WinGet/Packages/tinygo-org.tinygo_Microsoft.Winget.Source_8wekyb3d8bbwe/tinygo/bin"
    if [ -d "$TINYGO_WIN_BIN" ]; then
        PATH="$TINYGO_WIN_BIN:$PATH"
    fi
fi
export PATH

find_tool() {
    for cand in "$@"; do
        if command -v "$cand" >/dev/null 2>&1; then
            command -v "$cand"
            return 0
        fi
        if [ -x "$cand" ]; then
            echo "$cand"
            return 0
        fi
    done
    return 1
}

to_host_path() {
    if command -v cygpath >/dev/null 2>&1; then
        cygpath -m "$1"
    elif command -v wslpath >/dev/null 2>&1; then
        wslpath -m "$1"
    else
        echo "$1"
    fi
}

TINYGO_BIN="$(find_tool tinygo.exe tinygo "${TINYGO_WIN_BIN:-}/tinygo.exe")" || {
    echo "ERROR: tinygo not found in PATH"
    exit 1
}
NASM_BIN="$(find_tool nasm nasm.exe /mnt/c/mingw64/mingw64/bin/nasm.exe)" || {
    echo "ERROR: nasm not found in PATH"
    exit 1
}
OBJCOPY_BIN="$(find_tool objcopy objcopy.exe /mnt/c/mingw64/mingw64/bin/objcopy.exe)" || {
    echo "ERROR: objcopy not found in PATH"
    exit 1
}

NASM_OUT="$OUT/go_std_start.o"
NASM_SRC="$SVC/start.asm"
TINYGO_TARGET="$OUT/rugo-std-target.json"
TINYGO_OUT="$OUT/gostd.elf"
OBJCOPY_IN="$OUT/gostd.elf"
OBJCOPY_OUT="$OUT/gostd.bin"

if [[ "$NASM_BIN" == *.exe ]]; then
    NASM_OUT="$(to_host_path "$NASM_OUT")"
    NASM_SRC="$(to_host_path "$NASM_SRC")"
fi
if [[ "$TINYGO_BIN" == *.exe ]]; then
    TINYGO_TARGET="$(to_host_path "$TINYGO_TARGET")"
    TINYGO_OUT="$(to_host_path "$TINYGO_OUT")"
fi
if [[ "$OBJCOPY_BIN" == *.exe ]]; then
    OBJCOPY_IN="$(to_host_path "$OBJCOPY_IN")"
    OBJCOPY_OUT="$(to_host_path "$OBJCOPY_OUT")"
fi

echo "==> Assembling Go std spike startup stubs..."
"$NASM_BIN" -f elf64 -o "$NASM_OUT" "$NASM_SRC"

START_OBJ="$OUT/go_std_start.o"
LINKER_LD="$SVC/linker.ld"
if [[ "$TINYGO_BIN" == *.exe ]]; then
    START_OBJ="$(to_host_path "$START_OBJ")"
    LINKER_LD="$(to_host_path "$LINKER_LD")"
fi

cat > "$OUT/gostd-contract.env" <<EOF
GOOS=${CONTRACT_GOOS}
GOARCH=${CONTRACT_GOARCH}
TINYGO_COMPAT_GOOS=${COMPAT_GOOS}
EOF

cat > "$OUT/rugo-std-target.json" <<ENDJSON
{
	"llvm-target": "x86_64-unknown-none-elf",
	"cpu": "x86-64",
	"features": "+soft-float,-mmx,-sse,-sse2,-avx",
	"build-tags": ["rugo", "gostd_spike", "amd64"],
	"goos": "${COMPAT_GOOS}",
	"goarch": "${CONTRACT_GOARCH}",
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

echo "==> Building Go std spike binary with TinyGo..."
cd "$SVC"
"$TINYGO_BIN" build -target="$TINYGO_TARGET" -no-debug -o "$TINYGO_OUT" .

echo "==> Converting Go std spike ELF to flat binary..."
"$OBJCOPY_BIN" -O binary "$OBJCOPY_IN" "$OBJCOPY_OUT"
BIN_SIZE=$(stat -c%s "$OUT/gostd.bin" 2>/dev/null || stat -f%z "$OUT/gostd.bin" 2>/dev/null || wc -c < "$OUT/gostd.bin")
echo "==> Go std spike binary: $OUT/gostd.bin ($BIN_SIZE bytes)"
echo "==> Contract file: $OUT/gostd-contract.env (GOOS=${CONTRACT_GOOS}, GOARCH=${CONTRACT_GOARCH})"
