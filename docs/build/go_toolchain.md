# Go Toolchain for Kernel Code

## Strategy: gccgo (GCC Go frontend)

We use **gccgo** (the GCC Go frontend) instead of the standard `gc` compiler
because gccgo:

1. Produces standard ELF `.o` files that link directly with `ld`
2. Supports `-mcmodel=kernel` (critical for our higher-half kernel at
   `0xFFFFFFFF80000000`)
3. Supports `-mno-red-zone`, `-mno-sse`, and other x86-64 kernel ABI flags
4. Does not embed its own goroutine scheduler or full garbage collector into
   every object file

## Compiler flags

```
gccgo -c -fno-split-stack -mcmodel=kernel -mno-red-zone \
      -mno-sse -mno-mmx -mno-sse2 -O2 -fgo-pkgpath=kernelgo \
      kernelgo/entry.go -o out/go_entry.o
```

| Flag | Purpose |
|------|---------|
| `-c` | Compile only, produce `.o` |
| `-fno-split-stack` | Disable Go segmented/split stacks (we manage our own) |
| `-mcmodel=kernel` | Generate code for addresses above 0xFFFFFFFF80000000 |
| `-mno-red-zone` | Required for interrupt-safe kernel code on x86-64 |
| `-mno-sse -mno-mmx -mno-sse2` | No SIMD in kernel context |
| `-O2` | Optimisation level |
| `-fgo-pkgpath=kernelgo` | Sets the package path, controls symbol naming |

## Symbol naming

With `-fgo-pkgpath=kernelgo`, a Go function `func GoKmain() int64` produces
the ELF symbol `kernelgo.GoKmain`. The C bridge references it using GCC's
`__asm__` attribute:

```c
extern long GoKmain(void) __asm__("kernelgo.GoKmain");
```

## Runtime stubs

gccgo-compiled code may reference Go runtime helper symbols even for trivial
functions. We provide minimal stubs in `rtshim/runtime_stubs.c` that either
no-op or halt on panic. These stubs are added as the linker demands them.

## Build flow

```
kernelgo/entry.go  --[gccgo]--> out/go_entry.o
rtshim/bridge.c    --[gcc]----> out/bridge.o      (C-to-Go bridge)
rtshim/runtime_stubs.c --[gcc]-> out/runtime_stubs.o

All three are linked into kernel.elf alongside the other kernel objects.
```

## Docker

The build container (Ubuntu 24.04) installs `gccgo` via apt. See `Dockerfile`.
