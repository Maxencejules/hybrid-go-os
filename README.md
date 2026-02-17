# Rugo

A hybrid operating system: **Rust kernel** (low-level, no_std) + **Go services** (high-level, user space).

Target: x86-64, QEMU-first, Limine boot protocol.

## Architecture

- **Kernel (Rust):** Memory management, traps, scheduling, IPC, drivers — correctness-critical code in `no_std` Rust.
- **User space (Go):** Service manager, filesystem, package manager, network stack, shell — policy and ecosystem in Go (TinyGo short-term, full Go port long-term).

## Status

See [MILESTONES.md](MILESTONES.md) for the full roadmap.

A legacy C kernel implementation (M0-M7 complete, 16 tests passing) is preserved under `legacy/` for reference and fallback.

## Building

Prerequisites: Rust nightly toolchain, NASM, GNU ld, xorriso, QEMU, Python 3 + pytest.

```bash
make build    # compile kernel
make image    # build bootable ISO
make run      # boot in QEMU
make test-qemu # run acceptance tests
```

### Docker (cross-platform)

```bash
make docker-all
```

## Project layout

```
boot/           Limine config and linker script
kernel_rs/      Rust kernel crate (no_std, staticlib)
arch/x86_64/    Assembly: CPU entry, ISR stubs, context switch
legacy/         Legacy C kernel (M0-M7), preserved as reference
tools/          Image builders, QEMU runner, disk tools
tests/          Acceptance tests (pytest, marker-based)
```

## License

See individual files for licensing information.
