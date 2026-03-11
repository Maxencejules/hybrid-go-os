# Rugo

Rugo is a hybrid OS with a Rust `no_std` kernel and Go user space. The product
lane is the Rust kernel plus TinyGo-first services; the legacy C lane is kept
as a historical reference, and the stock-Go port remains experimental.

## What Matters First

| Lane | Status | Current source paths | Role |
|------|--------|----------------------|------|
| Hybrid OS | default | `arch/`, `boot/`, `kernel_rs/`, `services/go/` | Primary runtime: Rust kernel plus TinyGo-first user-space integration. |
| Experimental Go port | non-default | `services/go_std/`, `tools/build_go_std_spike.sh`, `tools/gostd_stock_builder/` | Stock-Go bring-up and ABI experiments. |
| Legacy baseline | reference only | `legacy/` | Historical C + gccgo implementation kept for comparison and regression context. |
| Support and validation | secondary | `tools/`, `tests/`, `docs/`, `.github/` | Build, packaging, CI, evidence collection, and acceptance gates. |

Architecture and repo strategy:
- overview: [docs/architecture/README.md](docs/architecture/README.md)
- target layout strategy: [docs/architecture/repo-strategy.md](docs/architecture/repo-strategy.md)
- current roadmap: [docs/roadmap/README.md](docs/roadmap/README.md)
- historical backlog/archive index: [docs/archive/README.md](docs/archive/README.md)

## Quick Start

```bash
make help         # show the primary developer workflows
make kernel       # build the Rust kernel ELF
make userspace    # build the default TinyGo userspace payload
make image-demo   # build the default demo ISO
make boot-demo    # boot the default demo ISO in QEMU
make smoke-demo   # boot + verify demo serial markers without Python
make gate-all     # full pytest-backed acceptance suite
make image-go-std # experimental stock-Go port image
```

Detailed build and host prerequisites live in [docs/BUILD.md](docs/BUILD.md).

## Architecture

The current source tree is still transitional, but the architectural split is
simple:

- Core runtime: `arch/`, `boot/`, `kernel_rs/`
- Userspace runtime: `services/go/`
- Tooling and support: `tools/`, `tests/`, `.github/`, `vendor/`
- Legacy and archive: `legacy/`, historical execution backlogs in `docs/`
- Experimental and research: `services/go_std/`, stock-Go builder tooling, and
  extended milestone research docs

The next structural step is to move toward an explicit `kernel/`,
`userspace/`, `support/`, `validation/`, and `experimental/` layout without
breaking the current build or test paths. That migration plan is documented in
[docs/architecture/repo-strategy.md](docs/architecture/repo-strategy.md).

## Milestone Status

| Track | What counts as progress | Current phase | Historical mapping |
|------|--------------------------|---------------|--------------------|
| Core Hybrid OS | The default Rust-kernel plus Go-service lane boots, runs native services, persists data, performs network I/O, and enforces runtime isolation on declared baseline targets. | `C5` complete; next core phase is `C6 Runtime Quality Under Load`. | `M0-M7`, `G1`, `M10`, `M12`, `M13`, `M16`, `M18`, `M19`, `M22`, `M25`, `M42` |
| Tooling / Validation / Release Infrastructure | Confidence, reproducibility, qualification, release, and fleet discipline around the core lane improve. | `T4` complete; next infrastructure phase is `T5 Advanced Trust and Compliance Infrastructure`. | `G2`, `M11`, `M14`, `M20`, `M21`, `M24`, `M28`, `M29`, `M30-M34`, `M40` |
| Expansion / Research / Platform Breadth | Compatibility, hardware breadth, desktop breadth, packaging breadth, and other product-surface expansion increase. | `X4` complete; next breadth phase is `X5 Next-Wave Breadth Research`. | `M8`, `M9`, `M15`, `M17`, `M23`, `M26`, `M27`, `M35-M39`, `M41`, `M43-M52` |

Primary scoring rule: the first row is the answer to "how close is the repo to
its stated goal?" `G1` should be read as the default TinyGo-first Go-service
lane. `G2` should be read as experimental stock-Go qualification, not as the
default product state.

For the exhaustive completion matrix, see [MILESTONES.md](MILESTONES.md). For
the detailed validation ledger that CI gates still reference, see
[docs/STATUS.md](docs/STATUS.md). For the three-track framework and rename
guidance, see [docs/roadmap/MILESTONE_FRAMEWORK.md](docs/roadmap/MILESTONE_FRAMEWORK.md).

## Demo And Validation Paths

- Recommended demo path: `make image-demo` then `make boot-demo`
  This is the clearest expression of the intended product direction: a Rust
  kernel booting a Go init task, a Go service manager, a Go shell, and a
  syscall-backed Go service.
- Non-Python demo smoke: `make smoke-demo`
  Verifies the canonical demo serial markers without going through pytest.
- Kernel-only smoke path: `make image-kernel` then `make boot-kernel`
  Useful when working on boot, paging, traps, or scheduler mechanics.
- Full acceptance suite: `make gate-all`
  This preserves the historical pytest-backed acceptance path and builds all
  current QEMU images, including TinyGo and stock-Go lanes.
- Stock-Go experiment: `make image-go-std`
  This remains an experimental porting lane, not the default repo story.

Compatibility aliases remain available: `make build`, `make image`,
`make run-kernel`, `make demo-go`, `make validate`, and `make test-qemu`.

## Detailed Docs

- Build guide: [docs/BUILD.md](docs/BUILD.md)
- Architecture overview: [docs/architecture/README.md](docs/architecture/README.md)
- Repo migration strategy: [docs/architecture/repo-strategy.md](docs/architecture/repo-strategy.md)
- Current roadmap and milestone streams: [docs/roadmap/README.md](docs/roadmap/README.md)
- Milestone framework: [docs/roadmap/MILESTONE_FRAMEWORK.md](docs/roadmap/MILESTONE_FRAMEWORK.md)
- Historical archive index: [docs/archive/README.md](docs/archive/README.md)
- Legacy lane notes: [legacy/README.md](legacy/README.md)

## Milestone Closure Records

Historical milestone backlogs remain available, but they are archive material
rather than the primary product narrative.

- M40 execution backlog (completed): `docs/M40_EXECUTION_BACKLOG.md`
- M41 execution backlog (completed): `docs/M41_EXECUTION_BACKLOG.md`
- M42 execution backlog (completed): `docs/M42_EXECUTION_BACKLOG.md`
- M43 execution backlog (completed): `docs/M43_EXECUTION_BACKLOG.md`
- M44 execution backlog (completed): `docs/M44_EXECUTION_BACKLOG.md`
- M45 execution backlog (completed): `docs/M45_EXECUTION_BACKLOG.md`
- M46 execution backlog (completed): `docs/M46_EXECUTION_BACKLOG.md`
- M47 execution backlog (completed): `docs/M47_EXECUTION_BACKLOG.md`
- M48 execution backlog (completed): `docs/M48_EXECUTION_BACKLOG.md`
- M49 execution backlog (completed): `docs/M49_EXECUTION_BACKLOG.md`
- M50 execution backlog (completed): `docs/M50_EXECUTION_BACKLOG.md`
- M51 execution backlog (completed): `docs/M51_EXECUTION_BACKLOG.md`
- M52 execution backlog (completed): `docs/M52_EXECUTION_BACKLOG.md`

Earlier completed backlogs for `M8-M39` are indexed in
[docs/archive/README.md](docs/archive/README.md).
