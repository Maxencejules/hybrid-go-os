# Process Model v3

Date: 2026-03-09  
Milestone: M36 Compatibility Surface Expansion v1  
Status: active release gate

## Objective

Define deterministic process and signal semantics required by
`compat_profile_v4`.

## Contract identifiers

- Process model contract ID: `rugo.process_model.v3`
- Parent compatibility profile ID: `rugo.compat_profile.v4`
- Surface campaign schema: `rugo.compat_surface_campaign_report.v1`

## Lifecycle model

States:

- `new`
- `ready`
- `running`
- `blocked`
- `zombie`
- `reaped`

Required transitions:

- `new -> ready`: admitted by scheduler.
- `ready -> running`: selected by scheduler.
- `running -> blocked`: waits on resource or syscall boundary.
- `blocked -> ready`: wait condition resolves.
- `running -> zombie`: process exits or receives terminal signal.
- `zombie -> reaped`: parent consumes child result via wait path.

## Required v3 checks

- `process_spawn_exec`: spawn-to-ready latency and deterministic startup.
- `process_wait_reap_once`: wait result consumable exactly once.
- `process_signal_fifo`: queued non-terminal signals preserve FIFO delivery.
- `process_sigkill_terminal`: `SIGKILL` transitions running task to terminal
  state with deterministic bounded latency.

Thresholds:

- spawn-to-ready latency: `<= 140 ms`
- wait/reap latency: `<= 25 ms`
- signal reorder events: `<= 2`
- SIGKILL terminal latency: `<= 45 ms`

## Deferred surface policy

- `fork` and `clone` parity are deferred in v3.
- Deferred process APIs must fail deterministically with `-1`, `ENOSYS`.
- Deferred behavior is release-blocking if it becomes non-deterministic.

## Tooling and gate wiring

- Campaign runner: `tools/run_compat_surface_campaign_v1.py`
- Local gate: `make test-compat-surface-v1`
- Local sub-gate: `make test-posix-gap-closure-v1`
- CI gate: `Compatibility surface v1 gate`
- CI sub-gate: `POSIX gap closure v1 gate`
