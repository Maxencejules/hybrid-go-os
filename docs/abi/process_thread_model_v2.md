# Process and Thread Model v2

Date: 2026-03-06  
Milestone: M16  
Lane: Rugo (Rust kernel + Go user space)  
Status: active release gate

## Goal

Define deterministic process/thread lifecycle semantics for mixed workloads with
explicit wait/kill ownership and fault containment behavior.

State machine identifier: `rugo.process_thread_model.v2`

## Scope

This contract freezes v2 behavior for:

- process/thread lifecycle states and transitions
- wait/kill semantics
- signal delivery ordering boundaries
- fault containment and scheduler survival requirements

## Lifecycle state model

States:

- `new`
- `ready`
- `running`
- `blocked`
- `exited`
- `reaped`

Required transitions:

- `new -> ready`: task is admitted to a runnable queue.
- `ready -> running`: task is selected by scheduler policy v2.
- `running -> blocked`: task waits on syscall/resource.
- `blocked -> ready`: wait condition resolves.
- `running -> exited`: explicit thread/process exit or terminal fault.
- `exited -> reaped`: parent observes termination via wait path.

## Wait/kill semantics v2

- `waitpid` remains deterministic for direct-child observations.
- A child exit event is consumable once; repeated waits return `-1` when no
  new waitable event exists.
- `kill(pid, SIGTERM)` requests graceful termination.
- `kill(pid, SIGKILL)` forces immediate terminal transition to `exited`.
- `wait/kill semantics` ownership is parent process policy, not scheduler
  policy.

## Default Go lane binding

- The default Go init/service manager uses `sys_wait` to block on child service
  exits.
- Reaped child slots can be reused for bounded restart attempts in the same
  boot session.
- Runtime-backed default-lane evidence:
  `tests/runtime/test_process_scheduler_runtime_v2.py`.

## Signal delivery boundaries

- Delivery order for normal queued signals is FIFO.
- `SIGKILL` is terminal and cannot be masked or deferred.
- Unknown signal ids are rejected with deterministic failure (`-1`).
- Queue overflow returns deterministic failure (`-1`) with no partial enqueue.

## Fault containment requirements

- Faulted user tasks are contained and transitioned to `exited`.
- Faulted user tasks are contained without scheduler collapse.
- Kernel execution must continue to a clean halt path for gate tests.

## Gate binding

- Local gate: `make test-process-scheduler-v2`
- CI gate: `.github/workflows/ci.yml` step `Process scheduler v2 gate`

## Executable references

- `tests/user/test_process_wait_kill_v2.py`
- `tests/user/test_signal_delivery_v2.py`
- `tests/runtime/test_process_scheduler_runtime_v2.py`
- `tests/sched/test_scheduler_gate_v2.py`
