# Core Runtime Backlog Closure

This document covers the backlog-bearing milestones that the roadmap maps into
the core runtime track. These are the milestones where the bar should be
strictest, because they directly affect the default Rust-kernel plus Go-service
lane.

The repo does have real anchors here: the monolithic kernel already boots,
enters user mode, supports syscalls and IPC, and exposes VirtIO block and basic
VirtIO net paths. The remaining gap is that many later core claims are broader
than the currently visible runtime path.

## Recommended Closure Order

1. Close `M10` and `M16` first. Per-object rights, transfer semantics, process
   objects, accounting, scheduler control, and wedged-service handling are the
   contract blockers for everything later.
2. Extend the existing manifest-driven `M25` runtime only. The current Go
   service manager is the one boot path later storage and network work should
   use.
3. Land `M12` and `M13` as the first real user-visible runtime expansion on
   that lane. That means usable sockets, address configuration, multi-flow
   networking, and real flush or fsync ordering with storage error surfacing.
4. Add boot-backed artifact collection before closing any v2 or soak milestone.
   `M18`, `M19`, and `M22` need evidence from the booted image, not only from
   deterministic gates.
5. Close `M18` and `M19` on top of the real v1 runtime by adding
   replay/journal/recovery, power-fail validation, concurrent sockets,
   retry/timeout behavior, and packet-trace-backed evidence.
6. Do `M22` next against real mixed block, network, and service workloads.
7. Finish `M42` last, after process, accounting, and service lifecycle
   semantics are stable enough that namespace/resource-control work will not be
   redesigned.

## C3: Contracted Service OS Runtime

| Backlog | Current class | Current repo reading | Literal implementation target | Still required |
|---|---|---|---|---|
| `M10 Security baseline v1` | `Runtime-partial` | Rights and filtering now cover both the M3 fd layer and the default Go lane's IPC/service-launch path, but storage, networking, and shared-memory rights are still not first-class end to end. | The default lane enforces capabilities or equivalent rights across handles, IPC, shared memory, storage, networking, and service launch. | Finish per-object rights for shared memory, storage, and networking, add explicit transfer semantics beyond the current owner-only R4 controls, and keep surfacing denial paths to the default Go services. |
| `M16 Process + Scheduler Model v2` | `Runtime-partial` | The default Go lane now uses kernel wait/reap semantics to block on child service exits, restart failed services, and reuse child slots on the real boot path, but there is still no fuller process-object model, resource accounting surface, or scheduler policy control plane. | The service OS has a stable process/thread lifecycle with wait, exit, blocking, wakeup, accounting, and scheduler behavior that the default Go lane truly depends on. | Add explicit process objects beyond the current task model, expose resource accounting and scheduler policy controls, and broaden recovery behavior from bounded service restarts to wedged-service detection and operator-visible control. |
| `M25 Userspace Service Model + Init v2` | `Runtime-backed` | `services/go/runtime.go` and `services/go/services.go` now boot the default Go lane through a manifest-driven service manager with phased startup, restart bookkeeping, lifecycle state logs, a live `diagsvc` control/diagnostic endpoint, and a boot-backed M25 gate. | The default Go lane boots through declarative service definitions with dependency ordering, restart policy, health state, logs, and IPC contracts. | Keep broadening this exact runtime toward real storage and networking services and keep later multi-service work on the same boot path instead of creating a new lane. |

## C4: Durable And Connected Runtime

| Backlog | Current class | Current repo reading | Literal implementation target | Still required |
|---|---|---|---|---|
| `M12 Network stack v1` | `Runtime-partial` | The kernel has a visible VirtIO net path and UDP echo behavior, but not a broad network-service implementation. | The default lane provides a real network stack or network service with interface configuration, routing, packet error handling, and a stable userspace API. | Move beyond UDP echo: implement usable socket semantics, address configuration, packet parsing/error surfacing beyond the smoke lane, multi-flow behavior, and wire the service into the manifest-driven Go runtime. |
| `M13 Storage reliability v1` | `Runtime-partial` | The kernel has real VirtIO block read/write syscalls, but the repo does not visibly show a complete durability implementation on the default Go lane. | The storage path exposes ordered writes, flush or fsync semantics, and error surfacing that the default filesystem and package flows actually use. | Wire flush ordering and fsync into the runtime, surface storage errors back to userspace, and validate that the default Go services observe real persistence behavior on live block state. |
| `M18 Storage reliability v2` | `Evidence-first` | The v2 storage lane is mostly contracts, model tests, and gates layered on top of the same narrow runtime block path. | The system survives power-fail and metadata-recovery scenarios using the real filesystem, real block queue, and real durability primitives. | Add replay/journal/recovery machinery, prove power-fail and metadata-ordering behavior on live state, exercise corruption/replay paths after reboot, and make the v2 tests boot and inspect actual runtime artifacts. |
| `M19 Network stack v2` | `Evidence-first` | The v2 network milestone adds broader docs and tests, but there is no equally broad visible runtime implementation in the default lane. | The system supports sustained network traffic, multi-socket behavior, timeout and retry handling, and service restart recovery beyond the echo path. | Handle multiple concurrent endpoints, add timeout/retry/restart behavior, and tie v2 evidence to real packet traces from the booted system. |

## C5: Reliable And Isolated Service OS

| Backlog | Current class | Current repo reading | Literal implementation target | Still required |
|---|---|---|---|---|
| `M22 Kernel Reliability + Soak v1` | `Runtime-partial` | The kernel is real, but the visible reliability lane is still dominated by deterministic artifact generation and bounded tests rather than obvious long-running mixed-service soak evidence. | The default lane runs for extended periods under mixed block, network, and service workloads without violating declared stability budgets. | Add long-run soak harnesses against the real booted image, stress mixed block/network/service workloads, collect runtime crash evidence, and measure restart or degradation budgets from the same lane the user actually boots. |
| `M42 Isolation + Namespace Baseline v1` | `Evidence-first` | The repo has namespace and cgroup contracts plus tests, but there is no equally visible namespace or resource-control implementation in the kernel. | The kernel enforces real containment, namespace separation, and resource-control semantics that the default services can rely on. | Add actual namespace primitives or a clearly scoped equivalent, implement resource controllers plus cleanup/observability, and land them only after process/accounting/service lifecycle controls are stable enough to avoid redesign. |

## Cross-Cutting Closure Work

- Finish the rights/process contract surface before trying to declare later
  storage, network, soak, or isolation milestones literal. Those later lanes
  need stable object and transfer rules to attach to.
- Split `kernel_rs/src/lib.rs` into explicit process, storage, networking,
  security, and isolation modules. The current monolith makes later core claims
  hard to reason about and harder to extend safely.
- Keep the new manifest-driven Go init/service runtime as the default lane and
  keep extending the same model to broader service sets instead of
  reintroducing one-off demo boot paths.
- Require `M18`, `M19`, and `M22` tests to boot the actual system and collect
  runtime artifacts before treating those milestones as literally closed. A
  core milestone should not be closable from schema-level evidence alone.
