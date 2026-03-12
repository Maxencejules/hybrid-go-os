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
supports syscalls and IPC, exposes block and network runtime surfaces, persists
journal-backed state across reboots, and boots the default Go lane through a
manifest-driven service runtime.

## Historical Closure Sequence

1. `M10` and `M16` closed the contract blockers first: rights enforcement,
   wait or reap semantics, deterministic scheduling behavior, and live service
   restart handling on the default lane.
2. `M25` then moved the default Go lane onto a manifest-driven init and service
   runtime instead of a one-off demo path.
3. `M12` and `M13` closed next as the first connected and durable runtime
   backlogs, but they closed with a mixed runtime-plus-contract evidence base.
4. `M18` and `M19` closed later in the ledger on top of that base and are now
   reinforced by the same boot-backed default lane.
5. `M22` and `M42` now close the sequence with runtime-backed reliability and
   isolation on the default lane.

## C3: Contracted Service OS Runtime

| Backlog | Backlog state | Implementation class | Closure basis in repo | Carry-forward product work |
|---|---|---|---|---|
| `M10 Security baseline v1` | `Closed` | `Runtime-backed` | Per-handle fd rights, rights reduction and transfer syscalls, syscall-filter policy, secure-boot manifest tooling, and default Go lane denial markers are all wired through executable kernel or `image-go` paths. | Extend the same capability language to shared-memory, block, and networking objects only if later core work needs that broader surface; that carry-forward work should not reopen the historical M10 backlog. |
| `M16 Process + Scheduler Model v2` | `Closed` | `Runtime-backed` | Deterministic scheduler v2 tests, kernel wait or reap semantics, and the boot-backed `tests/runtime/test_process_scheduler_runtime_v2.py` path make the shipped Go lane depend on real lifecycle and restart behavior. | Future work can add richer accounting, scheduler controls, or process objects, but that is additive runtime depth beyond the v2 closure contract already exercised by the default lane. |
| `M25 Userspace Service Model + Init v2` | `Closed` | `Runtime-backed` | `services/go/runtime.go` and `services/go/services.go` boot the default Go lane through a manifest-driven service manager with phased startup, restart bookkeeping, lifecycle state logs, a live `diagsvc` control endpoint, and a boot-backed M25 gate. | Keep extending this exact runtime toward real storage and networking services instead of opening alternate demo-only boot lanes. |

## C4: Durable And Connected Runtime

| Backlog | Backlog state | Implementation class | Closure basis in repo | Carry-forward product work |
|---|---|---|---|---|
| `M12 Network stack v1` | `Closed` | `Runtime-backed` | The kernel now exposes a real socket subsystem on the booted `image-go` lane, configures interfaces and routes, and exercises IPv6 stream-socket `bind/listen/connect/accept/send/recv` behavior from the default Go services. | Add broader datagram, timeout, and external-wire behavior only as additive network depth rather than as a reopened historical M12 task. |
| `M13 Storage reliability v1` | `Closed` | `Runtime-backed` | The default lane now opens durable runtime files, stages journal records on attached block media, replays them across reboot, and exposes ordered flush through `sys_fsync` on the live image. | Extend the same runtime into richer filesystem durability or corruption handling only as additive depth rather than as a reopened M13 task. |
| `M18 Storage reliability v2` | `Closed` | `Runtime-backed` | The v2 storage contracts and playbooks now sit on top of a live boot-backed journal/replay path, with `RECOV: replay ok` and `BLK: flush ordered` emitted by the running system and verified across two boots. | Add longer power-fail campaigns, metadata repair, or broader filesystem coverage only as additive runtime breadth. |
| `M19 Network stack v2` | `Closed` | `Runtime-backed` | The default `image-go` lane now configures IPv6 addresses and routes and drives multi-socket stream connection lifecycle through kernel socket syscalls, while the older interop and soak tooling remains supplementary evidence. | Add external interop, DNS breadth, and richer socket options only as additive network depth rather than as reopened backlog closure. |

## C5: Reliable And Isolated Service OS

| Backlog | Backlog state | Implementation class | Closure basis in repo | Carry-forward product work |
|---|---|---|---|---|
| `M22 Kernel Reliability + Soak v1` | `Closed` | `Runtime-backed` | The shipped `image-go` lane now runs boot-backed mixed service, storage, and socket workloads after journal replay, emits `SOAKC5: mixed ok`, and carries the earlier soak and fault tooling as supplementary evidence rather than as the only proof. | Extend the same path to longer-duration campaigns, broader fault classes, or external hardware soak only as additive reliability depth. |
| `M42 Isolation + Namespace Baseline v1` | `Closed` | `Runtime-backed` | The live kernel now applies per-service domains, capability flags, and fd/socket/endpoint limits, enforces owner-bound access on those objects, performs exit cleanup, and exposes isolation state through `sys_proc_info` plus `diagsvc` task snapshots on the booted lane. | Broader namespace or cgroup surface area can still be added later, but the historical M42 closure no longer depends only on synthetic host-side campaigns. |

## Cross-Cutting Closure Work

- The historical core-runtime backlog is closed in the flat ledger, and
  `M10`, `M12`, `M13`, `M16`, `M18`, `M19`, `M22`, `M25`, and `M42` are now
  runtime-backed closures for the default lane.
- `kernel_rs/src/runtime/` now exists as an explicit module boundary for
  process, storage, networking, security, and isolation helpers, but most
  subsystem logic still lives in `kernel_rs/src/lib.rs`; future core work
  should keep moving logic behind those modules instead of growing the
  monolith.
- Keep the manifest-driven Go init or service runtime as the default lane and
  extend that path when storage, networking, reliability, or isolation work
  becomes more literal.
- Treat `M22` and `M42` as closed historical backlogs whose default-lane
  runtime proof now exists; future reliability or containment breadth should
  land as additive depth rather than as a backlog reopen.
