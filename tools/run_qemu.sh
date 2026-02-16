#!/usr/bin/env bash
# Canonical QEMU runner for Hybrid Go OS
# Usage: ./tools/run_qemu.sh [--iso PATH]
#
# This is the single entry point for launching the OS in QEMU.
# Used by: make run, make test-qemu, CI workflows.

set -euo pipefail

ISO="${1:-out/os.iso}"

if [ ! -f "$ISO" ]; then
    echo "error: image not found at $ISO"
    echo "Run 'make image' first."
    exit 1
fi

# QEMU invocation from MILESTONES.md section 3.
# Adjust OVMF paths or remove pflash lines for BIOS-mode Limine boot.
exec qemu-system-x86_64 \
    -machine q35 \
    -cpu qemu64 \
    -m 1024 \
    -serial stdio \
    -display none \
    -no-reboot \
    -d int \
    -device isa-debug-exit,iobase=0xf4,iosize=0x04 \
    -cdrom "$ISO"
