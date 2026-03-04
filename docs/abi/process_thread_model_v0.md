# Process and Thread Model v0

## Lane

Rugo (Rust no_std kernel). This model applies to the Rugo lane only.

## G2 prep freeze window (active)

Freeze start: **2026-03-03**.

Freeze end: whichever comes first:
- **2026-03-17** (2 weeks from freeze start), or
- the second Rugo release cut after 2026-03-03.

During this window, behavior documented here is treated as
no-breaking-change contract.

## Scope

This document covers:
- task lifecycle states and transitions,
- thread spawn/exit behavior,
- scheduler guarantees and limits for current milestones.

## Model split by milestone path

### M3 user-mode path (single user task)

- Kernel enters one user task via `iretq`.
- Optional cooperative user threads can be created via `sys_thread_spawn`
  (M3/G2 path, max 4 threads per image).
- `sys_thread_exit` (nr `2`) terminates the current user task and returns
  to kernel halt path when no runnable user threads remain.
- In `thread_exit_test`, kernel emits `THREAD_EXIT: ok` before halt.
- User faults terminate the user task (`USER: killed`) and return to kernel.
- `sys_yield` is cooperative and switches to the next ready user thread when
  thread spawning is active; otherwise it returns `0`.

### R4 path (cooperative multi-task model)

Task states:
- `Ready`
- `Running`
- `Blocked`
- `Dead`

State transitions:
- `Ready -> Running`: selected by scheduler.
- `Running -> Ready`: `sys_yield`.
- `Running -> Blocked`: `sys_ipc_recv` when no message is available.
- `Blocked -> Ready`: message delivery to blocked waiter by `sys_ipc_send`.
- `Running -> Dead`: `sys_thread_exit` or user fault.

Exit behavior:
- `sys_thread_exit` kills current task and schedules next ready task.
- If no ready tasks remain, kernel exits test path (`r4_all_done`).

## Spawn semantics (v0)

M3/G2 cooperative path:
- `sys_thread_spawn` creates a runnable user thread in the current address space.
- `sys_yield` performs deterministic cooperative switching among ready threads.
- `sys_thread_exit` removes current thread; if no threads remain, kernel exits
  to halt path.

R4 quota-hardening path:
- In `quota_threads_test`, `sys_thread_spawn` validates entry address and enforces:
  - per-task limit: `MAX_THREADS_PER_PROC = 16`
  - global limit: `MAX_THREADS_GLOBAL = 64`
- Returns a synthetic thread id (`tid`) on success.

## Scheduler guarantees (v0)

- R4 scheduling is cooperative (not timer-preemptive).
- Runnable task selection is deterministic next-ready scan from
  `(current + 1) % R4_NUM_TASKS`.
- Context switches happen on:
  - `sys_ipc_recv` blocking path,
  - `sys_yield`,
  - task death (`sys_thread_exit` or user fault).

## Non-goals / limits in v0

- No POSIX-like process model.
- No general-purpose preemptive user scheduler.
- No complete preemptive thread lifecycle API (cooperative M3 + quota-focused R4 paths only).

## References

- `docs/abi/syscall_v0.md`
- `kernel_rs/src/lib.rs`
