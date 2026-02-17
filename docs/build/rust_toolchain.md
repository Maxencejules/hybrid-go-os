# Rust Toolchain for the Rugo Kernel

## Overview

The Rugo kernel (`kernel_rs/`) is a `no_std` Rust staticlib targeting
`x86_64-unknown-none`.  It is compiled with **nightly** Rust because it uses
`build-std` to compile `core` from source for the bare-metal target.

## rust-toolchain.toml

The repo root contains `rust-toolchain.toml`:

```toml
[toolchain]
channel = "nightly"
components = ["rust-src"]
```

`rustup` reads this file automatically and installs the correct nightly
toolchain plus the `rust-src` component (needed by `-Zbuild-std`).

## kernel_rs/.cargo/config.toml

```toml
[build]
target = "x86_64-unknown-none"

[target.x86_64-unknown-none]
rustflags = ["-C", "code-model=kernel", "-C", "relocation-model=static"]

[unstable]
build-std = ["core"]
build-std-features = ["compiler-builtins-mem"]
```

| Setting | Purpose |
|---------|---------|
| `target = "x86_64-unknown-none"` | Bare-metal x86-64, no OS, no libc |
| `code-model=kernel` | Addresses above `0xFFFFFFFF80000000` (higher-half) |
| `relocation-model=static` | No PIC/PIE — absolute addressing |
| `build-std = ["core"]` | Compile `core` from source for the target |
| `compiler-builtins-mem` | Provide `memcpy`/`memset`/`memcmp` implementations |

## Build pipeline

```
arch/x86_64/entry.asm  ──[nasm]──▶  out/entry.o
kernel_rs/src/lib.rs   ──[cargo]──▶  kernel_rs/target/x86_64-unknown-none/release/librugo_kernel.a

out/entry.o + librugo_kernel.a  ──[ld + boot/linker.ld]──▶  out/kernel.elf

out/kernel.elf + Limine  ──[xorriso + tools/mkimage.sh]──▶  out/os.iso
```

The root `Makefile` orchestrates all steps:

- `make build` — compiles entry.o, runs `cargo build --release`, links kernel.elf
- `make image` — fetches Limine (if needed), builds bootable ISO
- `make test-qemu` — boots the ISO in QEMU headless, runs pytest assertions

## Host dependencies

| Tool | Package (Ubuntu) | Purpose |
|------|-------------------|---------|
| nasm | `nasm` | Assemble x86-64 entry point |
| ld | `binutils` | Link kernel ELF |
| xorriso | `xorriso` | Create bootable ISO |
| git | `git` | Fetch Limine bootloader |
| make | `make` | Build orchestration |
| qemu-system-x86_64 | `qemu-system-x86` | Run smoke tests |
| python3 + pytest | `python3 python3-pytest` | Test assertions |
| rustup + nightly | `curl` + rustup.rs | Rust compiler |

All of these are installed automatically in CI (see `.github/workflows/ci.yml`)
and in the Docker build container (see `Dockerfile`).
