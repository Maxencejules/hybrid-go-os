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
# Rugo (build + QEMU smoke tests, 2 tests)
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
| **M1** Paging + traps | ✅ | ⬜ | `legacy/tests/boot/test_paging_enabled.py` (`MM: paging=on`), `legacy/tests/trap/test_page_fault_report.py` (`PF: addr=0x...`) |
| **M2** Scheduler + threads | ✅ | ⬜ | `legacy/tests/sched/test_timer_ticks.py` (`TICK: 100`), `legacy/tests/sched/test_two_threads.py` (interleaved `A`/`B`) |
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

The next Rugo milestone is **M1: Paging + traps**. This adds a physical memory
allocator (parsing the Limine memory map), initial page tables, a GDT, an IDT,
and exception handlers for page faults and GPF. The legacy implementation in
`legacy/kernel/vmm.c`, `legacy/kernel/pmm.c`, and `legacy/arch/x86_64/trap.c`
serves as the architectural reference.
