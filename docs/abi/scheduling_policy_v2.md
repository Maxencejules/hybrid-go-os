# Scheduling Policy v2

Date: 2026-03-06  
Milestone: M16  
Lane: Rugo (Rust kernel + Go user space)  
Status: active release gate

## Goal

Freeze deterministic scheduler v2 behavior for preemption, fairness, and soak
regression detection.

Scheduler policy identifier: `rugo.scheduling_policy.v2`

## Core policy

- Preemption is timer-driven and mandatory at quantum boundary.
- Default quantum: 3 ticks.
- Scheduling remains deterministic for identical workload + seed input.
- Deterministic tie-breaker: lowest `tid` for equal virtual runtime.

## Fairness rules

- Weighted fairness is enforced by priority classes:
  - `high`: weight `3`
  - `normal`: weight `2`
  - `low`: weight `1`
- Equal-priority runnable tasks must converge to near-equal service.
- Lower-priority tasks may receive less service, but starvation is disallowed.

## Soak and regression contract

- Soak campaigns must be reproducible from fixed seeds.
- Failure output must include machine-readable fields:
  - `schema`
  - `seed`
  - `ticks`
  - `timeline_digest`
  - `per_task`
  - `anomalies`
- Soak report schema: `rugo.scheduler_soak_report.v2`

## Process model integration

- Scheduler preemption/fairness policy consumes lifecycle states from
  `docs/abi/process_thread_model_v2.md`.
- Faulted user tasks are removed from runnable state and must not stall dispatch.

## Gate binding

- Local gate: `make test-process-scheduler-v2`
- CI gate: `.github/workflows/ci.yml` step `Process scheduler v2 gate`

## Executable references

- `tests/sched/test_preempt_timer_quantum_v2.py`
- `tests/sched/test_priority_fairness_v2.py`
- `tests/sched/test_scheduler_soak_v2.py`
- `tests/sched/test_scheduler_gate_v2.py`
