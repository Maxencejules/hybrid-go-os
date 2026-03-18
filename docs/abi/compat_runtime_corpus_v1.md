# Runtime Compatibility Corpus v1

Date: 2026-03-18  
Milestones: M8, M17, M27, M36, M41  
Status: active release gate

## Purpose

Ground the default compatibility lane in real binary execution instead of
contract-only evidence. This corpus runs bounded ET_EXEC ELF programs on the
default runtime surface and keeps unsupported edges explicit at the ABI
boundary.

Runtime compatibility corpus ID: `rugo.compat_runtime_corpus.v1`.

## Runtime lane

- Image: `out/os-compat-real.iso`
- Local gate: `make test-real-compat-runtime-v1`
- Runtime suite:
  - `tests/compat/test_real_compat_docs_v1.py`
  - `tests/compat/test_real_compat_suite_v1.py`
- Package bridge proof:
  - `tests/pkg/test_pkg_external_apps.py`

The corpus is booted from the same default Go-backed runtime lane used by
`image-go`, but the user payloads are real ELF binaries loaded by the runtime
loader instead of synthetic contract models.

## Corpus programs

### `x1-cli-file`

- Binary class: static ET_EXEC ELF.
- Markers:
  - `X1CLI: start`
  - `X1CLI: file ok`
- Required surfaces:
  - ELF loader acceptance on the default lane,
  - `open`, `read`, `close`,
  - `poll` readiness on `/compat/hello.txt` and `/dev/console`.

### `x1-proc-sock`

- Binary class: static ET_EXEC ELF.
- Markers:
  - `X1PROC: start`
  - `X1PROC: child ok`
  - `X1PROC: wait ok`
  - `X1SOCK: ok`
  - `X1DEFER: ok`
- Required surfaces:
  - `sys_thread_spawn` + `sys_wait`,
  - interface configuration and route install,
  - `socket_open`, `bind`, `listen`, `connect`, `accept`,
  - `send`, `recv`, `close`.

## Explicit deferred boundary

This corpus keeps explicit non-support behavior stable for deferred APIs:

- `fork` syscall slot `43` returns `-1`
- `clone` syscall slot `44` returns `-1`
- `epoll` syscall slot `45` returns `-1`

These probes are part of the runtime corpus itself, not only model-driven
negative tests.

## Package bridge

`tools/pkg_bootstrap_v1.py` now emits real ELF payloads for the external app
bootstrap lane. The package install path still bridges into `hello.pkg`, but
the runtime now detects ELF payloads, loads them through the same user loader,
and emits `PKG: elf ok` before execution.

## Scope limits

- This corpus proves a bounded compatibility subset, not full Linux ABI parity.
- Deferred surfaces stay explicit until a runtime implementation exists.
- New breadth claims must extend this corpus with additional real programs
  before profile scope expands.

## Related contracts

- `docs/abi/compat_profile_v2.md`
- `docs/abi/compat_profile_v3.md`
- `docs/abi/compat_profile_v4.md`
- `docs/abi/compat_profile_v5.md`
- `docs/pkg/package_format_v1.md`
