# Rugo — Status

## What this repo contains

| Track | Language | Location | Role |
|-------|----------|----------|------|
| **Rugo** | Rust (no_std) | repo root | Default build. Production rewrite target. |
| **Legacy** | C + Go (gccgo) | `legacy/` | Completed reference baseline (read-only). |

Full milestone definitions and acceptance criteria live in
[MILESTONES.md](../MILESTONES.md).

## How to run

```bash
# Rugo (build + QEMU smoke tests, 7 tests)
make test-qemu

# Legacy (build + QEMU smoke tests, 16 tests)
make -C legacy build && make -C legacy image && make -C legacy test-qemu

# Cross-platform via Docker
make docker-all
```

## Status matrix

| Milestone | Legacy | Rugo | Evidence |
|-----------|--------|------|----------|
| **M0** Boot + serial | ✅ | ✅ | `tests/boot/test_boot_banner.py` (`RUGO: boot ok`, `RUGO: halt ok`), `tests/boot/test_panic_path.py` (`RUGO: panic code=`). Legacy: `legacy/tests/boot/test_boot_banner.py` |
| **M1** Paging + traps | ✅ | ✅ | Rugo: `tests/boot/test_paging_enabled.py` (`MM: paging=on`), `tests/trap/test_page_fault_report.py` (`PF: addr=0x...`), `tests/trap/test_idt_smoke.py` (`TRAP: ok`). Legacy: `legacy/tests/boot/test_paging_enabled.py`, `legacy/tests/trap/test_page_fault_report.py` |
| **M2** Scheduler + threads | ✅ | ✅ | Rugo: `tests/sched/test_timer_ticks.py` (`TICK: 100`), `tests/sched/test_two_threads.py` (interleaved `A`/`B`). Legacy: `legacy/tests/sched/test_timer_ticks.py`, `legacy/tests/sched/test_two_threads.py` |
| **M3** User mode + syscalls | ✅ | ⬜ | `legacy/tests/user/test_enter_user_mode.py`, `test_syscall_roundtrip.py`, `test_user_fault.py` |
| **M4** IPC + shared memory | ✅ | ⬜ | `legacy/tests/ipc/test_ping_pong.py` (`PING: ok`, `PONG: ok`), `legacy/tests/ipc/test_shm_bulk.py` (`SHM: checksum ok`) |
| **M5** VirtIO block | ✅ | ⬜ | `legacy/tests/drivers/test_virtio_blk_identify.py`, `test_virtio_blk_rw.py` |
| **M6** Filesystem + pkg + shell | ✅ | ⬜ | `legacy/tests/fs/test_fsd_smoke.py` (`FSD: mount ok`), `legacy/tests/pkg/test_pkg_install_run.py` (`APP: hello world`) |
| **M7** VirtIO net + UDP | ✅ | ⬜ | `legacy/tests/net/test_udp_echo.py` (`NET: udp echo`) |
| **G0** Go kernel entry | ✅ | n/a | `legacy/tests/boot/test_go_entry.py` (`GO: kmain ok`). Legacy-only. |
| **G1** Go services (TinyGo) | n/a | ⬜ | Rugo-only. Depends on M3. |
| **G2** Full Go port | n/a | ⬜ | Rugo-only. Long-term. |

✅ done &ensp; ◐ partial &ensp; ⬜ not started &ensp; n/a not applicable

## Current focus

The next Rugo milestone is **M3: User mode + syscalls**. This adds ring-3
execution, per-process page tables, and the `int 0x80` syscall interface. The
legacy implementation in `legacy/kernel/user.c` and `legacy/kernel/syscall.c`
serves as the architectural reference.
