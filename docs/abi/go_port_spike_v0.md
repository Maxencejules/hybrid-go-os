# Go Port Spike v0 (G2)

## Purpose

Define a concrete G2 spike lane that:
- establishes the target contract (`GOOS=rugo`, `GOARCH=amd64`),
- documents runtime hook and syscall bridge requirements,
- produces a minimal user binary artifact that can feed
  `test_std_go_binary` (deterministic marker path).

## Target contract

- Contract GOOS: `rugo`
- Contract GOARCH: `amd64`

Artifact contract file:
- `out/gostd-contract.env`
- includes:
  - `GOOS=rugo`
  - `GOARCH=amd64`
  - `TINYGO_COMPAT_GOOS=...`

Current spike compiler bridge:
- `tools/build_go_std_spike.sh` uses TinyGo target JSON with
  `goarch=amd64`.
- `goos` is temporarily set via `SPIKE_COMPAT_GOOS` (default `linux`) until
  a native `GOOS=rugo` compiler/runtime path exists.
- This bridge is intentionally temporary; contract remains `GOOS=rugo`.

## Minimal spike binary target

- Source: `services/go_std/`
- Build script: `tools/build_go_std_spike.sh`
- Flat binary output: `out/gostd.bin`
- Kernel feature: `go_std_test`
- ISO target: `os-go-std.iso`
- Acceptance path: `tests/go/test_std_go_binary.py` (marker set: `GOSTD: ok`,
  `GOSTD: time ok`, `GOSTD: yield ok`, `THREAD_EXIT: ok`)

## Runtime hooks and glue points

### Implemented in spike lane

Entry and syscall glue:
- `services/go_std/rt0.asm`: `_start` -> calls `main`, then halts.
- `services/go_std/syscalls.asm`: syscall wrappers.
- `services/go_std/start.asm`: thin aggregator including the split assembly files.
- `main.sysDebugWrite` -> syscall `0` (`sys_debug_write`) via `int 0x80`.
- `main.sysThreadExit` -> syscall `2` (`sys_thread_exit`) via `int 0x80`.
- `main.sysYield` -> syscall `3` (`sys_yield`) via `int 0x80`.
- `main.sysTimeNow` -> syscall `10` (`sys_time_now`) via `int 0x80`.

Runtime/libc stubs used by TinyGo subset:
`services/go_std/runtime_stubs.asm`
- `runtime.alloc` (simple bump allocator)
- `getrandom`
- `tinygo_register_fatal_signals`
- `memset`, `memcpy`, `memmove`, `write`, `abort`, `exit`, `_exit`

### Required for full `GOOS=rugo` port (planned)

Runtime hook categories to replace spike stubs with real OS integration:
- startup/rt0 glue for rugo target (`rt0` + runtime init)
- thread creation/teardown hooks (`sys_thread_spawn`, `sys_thread_exit`)
- scheduler/yield hooks (`sys_yield`)
- monotonic time hooks (`sys_time_now`)
- virtual memory hooks (`sys_vm_map`, `sys_vm_unmap`)
- optional service hooks over IPC (`sys_ipc_*`, `sys_svc_*`) for stdlib integrations

## Syscall bridge map (v0)

| Go-facing bridge | ASM symbol | Syscall nr | Kernel ABI symbol |
|------------------|------------|------------|-------------------|
| debug write | `main.sysDebugWrite` | `0` | `sys_debug_write` |
| thread spawn (planned) | `main.sysThreadSpawn` | `1` | `sys_thread_spawn` |
| thread exit | `main.sysThreadExit` | `2` | `sys_thread_exit` |
| yield | `main.sysYield` | `3` | `sys_yield` |
| vm map (planned) | `main.sysVmMap` | `4` | `sys_vm_map` |
| vm unmap (planned) | `main.sysVmUnmap` | `5` | `sys_vm_unmap` |
| time now | `main.sysTimeNow` | `10` | `sys_time_now` |
| blk read (planned) | `main.sysBlkRead` | `13` | `sys_blk_read` |
| blk write (planned) | `main.sysBlkWrite` | `14` | `sys_blk_write` |
| net send (planned) | `main.sysNetSend` | `15` | `sys_net_send` |
| net recv (planned) | `main.sysNetRecv` | `16` | `sys_net_recv` |

Notes:
- Register convention remains as defined in `docs/abi/syscall_v0.md`.
- Return `-1` (`u64` all ones) is the uniform error contract.

## Replacement intent vs G1 path

G1 (`go_test`) remains the stable TinyGo bringup lane.

This spike lane (`go_std_test`) is intended to evolve until it can replace the
G1 binary path for the standard-go acceptance target:
- current marker set: `GOSTD: ok`, `GOSTD: time ok`, `GOSTD: yield ok`,
  `THREAD_EXIT: ok`
- eventual target: stock Go toolchain output for `GOOS=rugo`, `GOARCH=amd64`.
