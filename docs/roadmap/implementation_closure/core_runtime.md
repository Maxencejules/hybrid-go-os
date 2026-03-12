# Core Runtime Backlog Closure

This document records how the repo closed the historical core-runtime backlog
series that the roadmap maps into the default Rust-kernel plus Go-service lane.
The backlog itself is closed in the repo ledger; the tables below distinguish
that closure state from how literal each closure is in the shipped runtime.

A closed backlog row is not automatically a fully runtime-backed product claim.
Use the implementation class to tell the difference between:

- closures already exercised by booted kernel or Go-service code paths, and
- closures that still lean heavily on docs, models, host-side tooling, and gate
  wiring.

The repo does have real anchors here: the Rust kernel boots, enters user mode,
supports syscalls and IPC, exposes VirtIO block and basic VirtIO net paths, and
boots the default Go lane through a manifest-driven service runtime.

## Historical Closure Sequence

1. `M10` and `M16` closed the contract blockers first: rights enforcement,
   wait or reap semantics, deterministic scheduling behavior, and live service
   restart handling on the default lane.
2. `M25` then moved the default Go lane onto a manifest-driven init and service
   runtime instead of a one-off demo path.
3. `M12` and `M13` closed next as the first connected and durable runtime
   backlogs, but they closed with a mixed runtime-plus-contract evidence base.
4. `M18`, `M19`, `M22`, and `M42` closed later in the ledger on top of that
   base, and they remain the most evidence-heavy rows in literal
   implementation-closure terms.

## C3: Contracted Service OS Runtime

| Backlog | Backlog state | Implementation class | Closure basis in repo | Carry-forward product work |
|---|---|---|---|---|
| `M10 Security baseline v1` | `Closed` | `Runtime-backed` | Per-handle fd rights, rights reduction and transfer syscalls, syscall-filter policy, secure-boot manifest tooling, and default Go lane denial markers are all wired through executable kernel or `image-go` paths. | Extend the same capability language to shared-memory, block, and networking objects only if later core work needs that broader surface; that carry-forward work should not reopen the historical M10 backlog. |
| `M16 Process + Scheduler Model v2` | `Closed` | `Runtime-backed` | Deterministic scheduler v2 tests, kernel wait or reap semantics, and the boot-backed `tests/runtime/test_process_scheduler_runtime_v2.py` path make the shipped Go lane depend on real lifecycle and restart behavior. | Future work can add richer accounting, scheduler controls, or process objects, but that is additive runtime depth beyond the v2 closure contract already exercised by the default lane. |
| `M25 Userspace Service Model + Init v2` | `Closed` | `Runtime-backed` | `services/go/runtime.go` and `services/go/services.go` boot the default Go lane through a manifest-driven service manager with phased startup, restart bookkeeping, lifecycle state logs, a live `diagsvc` control endpoint, and a boot-backed M25 gate. | Keep extending this exact runtime toward real storage and networking services instead of opening alternate demo-only boot lanes. |

## C4: Durable And Connected Runtime

| Backlog | Backlog state | Implementation class | Closure basis in repo | Carry-forward product work |
|---|---|---|---|---|
| `M12 Network stack v1` | `Closed` | `Runtime-partial` | The kernel has a real VirtIO-net plus UDP-echo boot path and multi-machine QEMU checks, but the TCP, IPv6, poll, and soak semantics that closed the milestone are still mostly contract or model backed. | Promote socket semantics, address configuration, and packet-error handling into booted runtime paths if the architecture-first scoreboard needs a fully literal connected-runtime story. |
| `M13 Storage reliability v1` | `Closed` | `Runtime-partial` | The block path and mount baseline are real, while durability classes, recovery reports, and fault campaigns that closed the backlog are still largely host-side tooling plus image validation. | Tie fsync or flush ordering and recovery behavior to live block state from booted images before treating storage durability as fully runtime-backed. |
| `M18 Storage reliability v2` | `Closed` | `Evidence-first` | The v2 storage backlog closed through stronger contracts, recovery and power-fail generators, and gate wiring layered on the same narrow storage runtime. | Real journal or replay machinery, reboot-after-corruption evidence, and boot-backed recovery artifacts are still the carry-forward work if C4 is to become literal at runtime. |
| `M19 Network stack v2` | `Closed` | `Evidence-first` | The v2 network backlog closed through broader contracts, interop or soak tooling, DNS-stub checks, and gate wiring, while the live booted network runtime still visibly bottoms out near the earlier echo path. | Multi-socket runtime behavior, timeout or retry handling, and packet-trace-backed evidence from the booted system remain the carry-forward work. |

## C5: Reliable And Isolated Service OS

| Backlog | Backlog state | Implementation class | Closure basis in repo | Carry-forward product work |
|---|---|---|---|---|
| `M22 Kernel Reliability + Soak v1` | `Closed` | `Evidence-first` | The backlog closed through deterministic soak and fault tooling, schema checks, and release-gate wiring rather than through long-running mixed-service campaigns emitted by a booted image. | Long-run boot-backed soak artifacts and mixed block, network, and service workloads remain the carry-forward product work if the repo wants literal reliability claims. |
| `M42 Isolation + Namespace Baseline v1` | `Closed` | `Evidence-first` | The backlog closed through namespace or cgroup contracts, synthetic isolation campaigns, negative-path gates, and the smaller real quota or owner-right controls already present in the kernel. | Literal namespaces, cgroups, cleanup, and observability in the live kernel remain the carry-forward work; they should land as fresh runtime depth, not as a reopened historical closure task. |

## Cross-Cutting Closure Work

- The historical core-runtime backlog is closed in the flat ledger, but only
  `M10`, `M16`, and `M25` are already strong runtime-backed closures for the
  default lane.
- `kernel_rs/src/runtime/` now exists as an explicit module boundary for
  process, storage, networking, security, and isolation helpers, but most
  subsystem logic still lives in `kernel_rs/src/lib.rs`; future core work
  should keep moving logic behind those modules instead of growing the
  monolith.
- Keep the manifest-driven Go init or service runtime as the default lane and
  extend that path when storage, networking, reliability, or isolation work
  becomes more literal.
- Treat `M12`, `M13`, `M18`, `M19`, `M22`, and `M42` as closed historical
  backlogs with carried-forward runtime depth work, not as still-open execution
  backlogs.
