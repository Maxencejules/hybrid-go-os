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
- `sys_thread_exit` (nr `2`) terminates the current user task and returns
  to kernel halt path.
- In `thread_exit_test`, kernel emits `THREAD_EXIT: ok` before halt.
- User faults terminate the user task (`USER: killed`) and return to kernel.
- `sys_yield` returns `0`; it does not provide user-mode task switching in this path.

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

`sys_thread_spawn` is currently quota-focused, not a full thread creator:
- In `quota_threads_test`, validates entry address and enforces:
  - per-task limit: `MAX_THREADS_PER_PROC = 16`
  - global limit: `MAX_THREADS_GLOBAL = 64`
- Returns a synthetic thread id (`tid`) on success.
- Outside `quota_threads_test`, returns `-1` (stub behavior).

No runnable thread object is created by `sys_thread_spawn` in current v0.

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
- No complete thread lifecycle API (spawn is partial, quota-oriented).

## References

- `docs/abi/syscall_v0.md`
- `kernel_rs/src/lib.rs`
