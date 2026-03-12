# M16 Execution Backlog (Process + Scheduler Model v2)

Date: 2026-03-06  
Lane: Rugo (Rust kernel + Go user space)  
Status: done

## Goal

Upgrade process and scheduler behavior from baseline to deterministic preemption,
fairness, and lifecycle handling for mixed workloads.

M16 source of truth remains `docs/M15_M20_MULTIPURPOSE_PLAN.md`,
`MILESTONES.md`, and this backlog.

## Current State Summary

- Core scheduling and user-mode milestones are already complete.
- M16 is the v2 stabilization point for process/thread semantics.
- Scheduler v2 gate is now wired in local and CI release lanes.
- The default Go lane now blocks in `sys_wait`, reaps exited service tasks, and
  reuses child slots for bounded restart attempts on real `image-go` boots.

## Execution Result

- PR-1: complete (2026-03-06)
- PR-2: complete (2026-03-06)
- PR-3: complete (2026-03-06)
- Runtime-backed closure addendum: complete (2026-03-12)

## PR-1: Process/Thread Contract v2

### Objective

Freeze process lifecycle and scheduling policy contracts before deeper behavior
hardening.

### Scope

- Add docs:
  - `docs/abi/process_thread_model_v2.md`
  - `docs/abi/scheduling_policy_v2.md`
- Add tests:
  - `tests/user/test_process_wait_kill_v2.py`
  - `tests/user/test_signal_delivery_v2.py`

### Primary files

- `docs/abi/process_thread_model_v2.md`
- `docs/abi/scheduling_policy_v2.md`
- `tests/user/test_process_wait_kill_v2.py`
- `tests/user/test_signal_delivery_v2.py`

### Acceptance checks

- `python -m pytest tests/user/test_process_wait_kill_v2.py tests/user/test_signal_delivery_v2.py -v`

### Done criteria for PR-1

- Process/thread semantics are versioned and test-referenced.
- Lifecycle edge cases have explicit ownership and behavior.

## PR-2: Scheduler Behavior + Fairness

### Objective

Make preemption, fairness, and soak behavior deterministic and regression-safe.

### Scope

- Add tests:
  - `tests/sched/test_preempt_timer_quantum_v2.py`
  - `tests/sched/test_priority_fairness_v2.py`
  - `tests/sched/test_scheduler_soak_v2.py`
- Add helper model:
  - `tests/sched/v2_model.py`

### Primary files

- `tests/sched/test_preempt_timer_quantum_v2.py`
- `tests/sched/test_priority_fairness_v2.py`
- `tests/sched/test_scheduler_soak_v2.py`
- `tests/sched/v2_model.py`

### Acceptance checks

- `python -m pytest tests/sched/test_preempt_timer_quantum_v2.py tests/sched/test_priority_fairness_v2.py tests/sched/test_scheduler_soak_v2.py -v`

### Done criteria for PR-2

- Preemption/fairness behavior is deterministic across seeds/runs.
- Soak regressions are detectable with machine-readable failure output.

## PR-3: Scheduler Gate + Milestone Closure

### Objective

Promote scheduler v2 checks to required local and CI gates.

### Scope

- Add aggregate test:
  - `tests/sched/test_scheduler_gate_v2.py`
- Add local gate:
  - `Makefile` target `test-process-scheduler-v2`
- Add CI gate:
  - `.github/workflows/ci.yml` step `Process scheduler v2 gate`

### Primary files

- `tests/sched/test_scheduler_gate_v2.py`
- `Makefile`
- `.github/workflows/ci.yml`
- `MILESTONES.md`
- `docs/STATUS.md`

### Acceptance checks

- `make test-process-scheduler-v2`

### Done criteria for PR-3

- Scheduler v2 gate is release-blocking in local and CI lanes.
- M16 status can be marked done with linked gate evidence.

## Runtime-backed closure addendum

### Objective

Bind M16 lifecycle semantics to the default Go boot lane instead of leaving the
milestone entirely model and gate driven.

### Scope

- Extend the R4 kernel path with wait/reap semantics for direct-child exits.
- Reuse reaped child slots for bounded service restart attempts.
- Add boot-backed evidence:
  - `tests/runtime/test_process_scheduler_runtime_v2.py`
- Update the local M16 gate so it builds and boots `image-go`.

### Primary files

- `kernel_rs/src/lib.rs`
- `services/go/runtime.go`
- `services/go/services.go`
- `services/go/start.asm`
- `services/go/syscalls.go`
- `tests/runtime/test_process_scheduler_runtime_v2.py`
- `Makefile`

### Acceptance checks

- `make test-process-scheduler-v2`

### Done criteria

- The default Go init/service lane blocks in `sys_wait` for child exits.
- Reaped child slots are reused during bounded restart on the live boot path.
- M16 gate coverage includes the real `image-go` boot evidence.

## Non-goals for M16 backlog

- Full scheduler class parity with large production kernels.
- NUMA-aware scheduling unless explicitly re-scoped.
