# Hybrid Go OS: Repo-ready Milestones, Issues, and Acceptance Tests

Date: 2026-02-16
Defaults assumed: x86-64, QEMU-first, Limine boot protocol, freestanding C userland first (init + early servers), Go-heavy services later.

This file is meant to be dropped into your repo as `MILESTONES.md` and used as a checklist to create GitHub issues. It includes:
- Recommended labels
- Milestone plan (M0 to M6)
- Issue-sized tasks with clear definitions of done
- Acceptance tests designed for automated QEMU CI

---

## 1) Recommended GitHub labels

Core
- `area:boot`
- `area:arch-x86_64`
- `area:mm` (memory management)
- `area:trap` (interrupts, exceptions, syscalls)
- `area:sched`
- `area:ipc`
- `area:userland`
- `area:drivers`
- `area:storage`
- `area:net`
- `area:tooling`
- `area:ci`

Priority
- `p0` must land to boot
- `p1` needed for user mode and syscalls
- `p2` needed for ecosystem slice (drivers, fs, pkg)
- `p3` networking and later features

Status
- `status:blocked`
- `status:needs-design`
- `status:needs-review`

---

## 2) Repo layout (proposal)

Keep early structure simple and stable:

```
/boot/                 # Limine config, linker scripts, kernel image packaging
/kernel/               # Kernel code (target: mostly Go). Early M0 may include C while Go bootstraps.
/rtshim/               # minimal runtime integration layer (Go runtime support glue)
/arch/x86_64/          # asm stubs: entry, isr/syscall stubs, context switch
/user/                 # userland programs (start: freestanding C)
/services/             # user space servers: drvman, blkdevd, fsd, pkgd, netd
/tools/                # mkimage, packager, qemu runners
/tests/                # boot tests, syscall tests, service tests
/.github/workflows/    # CI (QEMU headless boot + test harness)
```

---

## 3) Test philosophy

All acceptance tests should:
- Run in QEMU headless (serial console).
- Emit deterministic log lines.
- Exit QEMU with a non-zero code on failure (use `isa-debug-exit`).
- Avoid manual inspection.

### Suggested QEMU runner baseline

Example (adjust paths to your build outputs):
```
qemu-system-x86_64 \
  -machine q35 \
  -cpu qemu64 \
  -m 1024 \
  -serial stdio \
  -display none \
  -no-reboot \
  -d int \
  -device isa-debug-exit,iobase=0xf4,iosize=0x04 \
  -drive if=pflash,format=raw,readonly=on,file=OVMF_CODE.fd \
  -drive if=pflash,format=raw,file=OVMF_VARS.fd \
  -cdrom out/os.iso
```

For early milestones, you can skip UEFI and boot via Limine BIOS mode if that is what you choose. Keep one canonical runner in `tools/run_qemu.sh` and reuse it in CI.

---

## 4) Milestones overview

M0: Boot + serial logging (C/asm OK)
G0: First Go kernel entry executes (Go+rtshim+linking)
M1: Paging + traps (IDT) in Go kernel (asm stubs remain) + page fault reporting
M2: Scheduler + kernel threads
M3: User mode + syscall ABI v0
M4: IPC + shared memory + service discovery v0
M5: User space drivers (VirtIO block first) + block service
M6: Filesystem service + package manager + shell runs a packaged app
Optional M7: VirtIO net + net service + minimal UDP demo

Each milestone has:
- Definition of done
- Issues (issue-sized)
- Acceptance tests (automatable)

---

## M0: Boot + serial logging

### Definition of done
- System boots in QEMU to kernel.
- Serial output prints a banner and halts cleanly.
- Panic path prints a reason code and halts.

### Issues
- [ ] (p0, area:boot) Create Limine bootable image skeleton
  - Deliverables: `limine.cfg`, ISO build script, kernel ELF packaging
- [ ] (p0, area:arch-x86_64) Implement `_start` and a minimal stack setup in asm
- [ ] (p0, area:tooling) Add `tools/mkimage` or script to produce `out/os.iso`
- [ ] (p0, area:boot) Implement early serial logging (COM1) write function
- [ ] (p0, area:tooling) Add `tools/run_qemu.sh` and a one-command `make run`

### Acceptance tests
- `tests/boot/test_boot_banner.py`
  - Run QEMU, assert serial contains:
    - `KERNEL: boot ok`
    - `KERNEL: halt ok`
- `tests/boot/test_panic_path.py`
  - Force a controlled panic (compile-time flag)
  - Assert serial contains:
    - `KERNEL: panic code=...`
  - Assert QEMU exits via debug-exit with failure code


---

## G0: First Go kernel entry executes (Go + rtshim + linking)

### Purpose
Make the kernel able to execute **real Go code** in kernel context, while keeping the low-level entry/exit in asm.
This avoids mixing "bring up Go runtime/linking" with "bring up paging/IDT" in the same milestone.

### Definition of done
- Kernel image contains Go code and successfully jumps into a Go entry point.
- A minimal runtime integration layer (`/rtshim`) reserves a Go heap region and supports basic Go execution.
- Serial output proves Go ran by printing a deterministic marker.
- M0 tests still pass unchanged.

### Issues
- [ ] (p0, area:tooling) Add Go cross-build toolchain wiring to the build system
  - Goal: produce Go object/archive suitable for linking into `kernel.elf`
  - Deliverables: documented build steps in `docs/build/go_toolchain.md`
- [ ] (p0, area:rtshim) Implement minimal runtime integration layer v0
  - Reserve heap region early
  - Provide any required runtime stubs/glue for bare-metal start
  - Keep trap/interrupt paths allocation-free
- [ ] (p0, area:arch-x86_64) Add an asm-to-Go jump glue
  - Call a Go entry symbol (for example `kmain_go`)
- [ ] (p0, area:boot) Ensure serial logging works from Go path (reuse the C serial driver or expose a tiny call boundary)

### Acceptance tests
- `tests/boot/test_go_entry.py`
  - Run QEMU, assert serial contains:
    - `GO: kmain ok`
  - Assert M0 markers are still present:
    - `KERNEL: boot ok`
    - `KERNEL: halt ok`

Notes (why this milestone exists):
- Kernels written primarily in Go have been demonstrated (e.g., Biscuit), but they rely on a runtime strategy and low-level assembly stubs.


## M1: Paging + traps + page fault reporting (Go kernel)

### Definition of done
- Paging enabled with a known kernel mapping strategy (higher-half or identity + higher-half).
- IDT installed; page fault handler prints fault address and error bits, then halts or recovers for known cases.
- Go kernel code (already proven in G0) continues to run reliably after paging is enabled.

### Issues
- [ ] (p0, area:mm) Parse bootloader memory map and build a physical page allocator
- [ ] (p0, area:mm) Build initial page tables and enable paging
- [ ] (p0, area:trap) Install GDT and IDT
- [ ] (p0, area:trap) Exception handlers: page fault, general protection fault, double fault (halt path)
- [ ] (p1, area:mm) Move paging/mm logic into Go kernel modules (asm remains for CR3 writes, etc.)
- [ ] (p1, area:trap) Trap dispatch table in Go (asm stubs only save/restore + jump)
- [ ] (p1, area:rtshim) Minimal runtime integration layer v0
  - No allocation in trap context
  - Preallocated per-CPU data structures
- [ ] (p1, area:tooling) Add symbol map export for debugging (`nm`, `objdump` helpers)

### Acceptance tests
- `tests/boot/test_paging_enabled.py`
  - Assert serial contains `MM: paging=on`
- `tests/trap/test_page_fault_report.py`
  - Trigger known page fault in kernel mode
  - Assert serial contains `PF: addr=... err=...`
- `tests/trap/test_idt_smoke.py`
  - Trigger a breakpoint or divide-by-zero
  - Assert handler prints and halts cleanly

---

## M2: Scheduler + kernel threads

### Definition of done
- Timer interrupts tick.
- Kernel can run at least two kernel threads and switch between them.
- Basic synchronization primitive exists (spinlock or mutex) without deadlocking under timer interrupts.

### Issues
- [ ] (p1, area:trap) Timer interrupt source configured (PIT or APIC timer)
- [ ] (p1, area:sched) Scheduler core: runnable queue, thread states
- [ ] (p1, area:arch-x86_64) Context switch primitive (save/restore)
- [ ] (p1, area:sched) Per-CPU idle thread
- [ ] (p1, area:sched) Basic lock primitive + rule for interrupt masking

### Acceptance tests
- `tests/sched/test_timer_ticks.py`
  - Assert serial contains `TICK: 100` within a time budget
- `tests/sched/test_two_threads.py`
  - Create two kernel threads that print `A` and `B`
  - Assert interleaving output `A...B...A...B...` occurs

---

## M3: User mode + syscall ABI v0

### Definition of done
- Kernel creates a user address space, loads a tiny user program, and enters ring 3.
- User program can invoke syscalls and return to user mode safely.
- Minimal syscall set is present and documented.

### Syscall ABI v0 (minimum)
- `sys_debug_write`
- `sys_thread_spawn`, `sys_thread_exit`, `sys_yield`
- `sys_vm_map`, `sys_vm_unmap`
- `sys_shm_create`, `sys_shm_map`
- `sys_ipc_send`, `sys_ipc_recv`
- `sys_time_now`

### Issues
- [ ] (p1, area:mm) Per-process page tables and user mappings
- [ ] (p1, area:trap) Syscall entry/exit path (syscall/sysret or int gate)
- [ ] (p1, area:userland) Minimal freestanding C runtime stubs for user programs
- [ ] (p1, area:userland) `init` user program that prints and yields
- [ ] (p1, area:tooling) Document syscall numbers and structures in `docs/abi/syscall_v0.md`

### Acceptance tests
- `tests/user/test_enter_user_mode.py`
  - Assert serial contains `USER: hello`
- `tests/user/test_syscall_roundtrip.py`
  - User calls `sys_debug_write` and `sys_time_now`
  - Assert kernel prints `SYSCALL: ok`
- `tests/user/test_user_fault.py`
  - Trigger user page fault
  - Assert kernel terminates that task and continues running init

---

## M4: IPC + shared memory + service discovery v0

### Definition of done
- Two user processes can exchange messages through kernel IPC endpoints.
- Shared memory handle can be created and mapped by two processes.
- A minimal service registry exists so clients can locate servers by name.

### Issues
- [ ] (p1, area:ipc) IPC endpoint object and message queue
- [ ] (p1, area:ipc) Blocking receive with wakeups
- [ ] (p1, area:mm) Shared memory objects with handle table integration
- [ ] (p2, area:userland) Service registry process `svcman` (or kernel registry v0)
- [ ] (p2, area:userland) Client library for IPC + service lookup

### Acceptance tests
- `tests/ipc/test_ping_pong.py`
  - Spawn `ping` and `pong` processes
  - Assert `PING: ok` and `PONG: ok`
- `tests/ipc/test_shm_bulk.py`
  - Writer fills shared region; reader verifies checksum
  - Assert `SHM: checksum ok`

---

## M5: User space drivers (VirtIO block first) + block service

### Definition of done
- VirtIO block device works in QEMU.
- A user space driver server `blkdevd` handles interrupts and performs read/write to the device.
- A stable block service API exists over IPC with shared memory for data.

### Issues
- [ ] (p2, area:drivers) VirtIO device discovery and capability model for mapping MMIO or queues
- [ ] (p2, area:drivers) Interrupt delivery to driver server (event IPC)
- [ ] (p2, area:drivers) `blkdevd` user space server: init, request loop, read/write ops
- [ ] (p2, area:storage) Block service protocol v0
- [ ] (p2, area:ci) Add QEMU configuration for virtio-blk and a disk image in tests

### Acceptance tests
- `tests/drivers/test_virtio_blk_identify.py`
  - Assert `BLK: found virtio-blk`
- `tests/drivers/test_virtio_blk_rw.py`
  - Write a block pattern, read back, verify hash
  - Assert `BLK: rw ok`

---

## M6: Filesystem service + package manager + shell runs a packaged app

### Definition of done
- `fsd` provides path-based open, read, write (minimal) using the block service as backing store.
- `pkg` can install a package from local media into a package store.
- `sh` can launch an installed app that prints output.

### Issues
- [ ] (p2, area:storage) Filesystem format choice for v0 (simple custom or existing small FS)
- [ ] (p2, area:storage) `fsd` server: mount, open, read, write, list
- [ ] (p2, area:tooling) Package format v0: manifest + payload archive
- [ ] (p2, area:userland) `pkg` tool: install, remove, list
- [ ] (p2, area:userland) `sh` minimal shell: run, ls, cat, echo
- [ ] (p2, area:ci) Integration test image builder that includes a sample package

### Acceptance tests
- `tests/fs/test_fsd_smoke.py`
  - `fsd` mounts and lists root
  - Assert `FSD: mount ok`
- `tests/pkg/test_pkg_install_run.py`
  - Install `hello.pkg`
  - Run `hello`
  - Assert `APP: hello world`

---

## Optional M7: VirtIO net + net service + minimal UDP demo

### Definition of done
- VirtIO net device works in QEMU.
- `netd` can send and receive packets.
- Minimal UDP echo demo works (host-to-guest or guest-to-guest).

### Issues
- [ ] (p3, area:drivers) `netdevd` VirtIO net driver server
- [ ] (p3, area:net) `netd` network stack server (start: raw frames, then UDP)
- [ ] (p3, area:net) UDP echo demo app
- [ ] (p3, area:ci) QEMU networking setup for tests

### Acceptance tests
- `tests/net/test_udp_echo.py`
  - Send UDP packet to guest
  - Assert echo received and logged

---

## 5) GitHub issue template (copy-paste)

Create `.github/ISSUE_TEMPLATE/task.md`:

```
---
name: Task
about: Single deliverable with acceptance test
title: "[M?] <short title>"
labels: ["p?", "area:<...>"]
---

## Goal
Describe the end state in one sentence.

## Deliverables
- [ ] Code
- [ ] Docs
- [ ] Tests

## Definition of done
- [ ] Acceptance test passes: <tests/...>

## Notes
Constraints, ABI notes, or links to spec pages.
```

---

## 6) CI workflow outline (QEMU smoke)

- Build kernel + image in CI
- Run QEMU headless
- Parse serial output
- Fail if expected markers are missing

Minimal workflow steps:
1. `make build`
2. `make image`
3. `make test-qemu` (runs selected tests)

---

If you want, I can also generate a starter `tests/` harness structure and a sample `test_boot_banner.py` that launches QEMU, captures serial, and asserts expected output.
