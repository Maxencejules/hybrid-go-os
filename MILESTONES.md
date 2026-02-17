# Rugo Milestone Plan: Rust Kernel (low-level) + Go Services (high-level)

Date: 2026-02-17
Target: x86-64, QEMU-first, Limine boot protocol

Intent:
- Rust owns kernel mechanisms (correctness-critical, no_std).
- Go owns high-level user space services and the ecosystem.
- Go Track A (TinyGo-first) is the short-term path to get Go services running.
- Go Track B (full Go port) is explicitly long-term and should start only after the kernel ABI/process model stabilizes.

---

## 0) Key constraints and design choices

### Rust kernel target and no_std stance
- Kernel code is Rust `no_std` (often also `no_main`) compiled for a bare-metal target such as `x86_64-unknown-none`.
- A thin assembly layer still exists for CPU entry, trap stubs, and context switch glue.

### Go in user space, not kernel
- Go is used for high-level services in user space (fsd, pkgd, netd, svcman).
- Running standard Go binaries on a new OS is a porting effort (a new GOOS/GOARCH combination). This is not the short-term path.

### Go track decision (explicit)
Track A: TinyGo-first (short-term)
- Goal: get 1-3 Go services running early with a constrained subset of Go/stdlib.
- Expectation: avoid heavy reflection patterns; keep deps minimal.
- Outcome: usable Go ecosystem inside your OS earlier.

Track B: Full Go port (long-term)
- Goal: run standard Go binaries produced by the stock toolchain (a real GOOS/GOARCH port).
- Start condition: syscall ABI and process model have stopped changing frequently; you are ready to maintain a stable runtime contract.
- Outcome: standard Go runtime and toolchain support for your OS.

---

## 1) Architecture boundary

### Kernel (Rust) provides mechanisms
- Memory management: physical allocator, paging, per-process page tables
- Traps: IDT, exception handling, syscall entry dispatch
- Scheduling: threads, runnable queues, timers
- IPC and shared memory primitives
- Security boundary: handle table or capabilities
- Minimal drivers required to boot and test under QEMU (VirtIO preferred early)

### User space (Go services) provides policy and ecosystem
- Service manager: svcman
- Filesystem service: fsd
- Package manager: pkg and pkgd
- Network stack service: netd
- Shell and core utilities

---

## 2) Milestone overview

M0: Boot and serial logging (asm + Rust entry)
R1: Paging + traps (IDT) + page fault reporting (Rust)
R2: Scheduler + kernel threads (Rust)
R3: User mode + syscall ABI v0 (Rust kernel, C or Rust userland)
R4: IPC + shared memory + service registry v0
R5: QEMU drivers: VirtIO block in kernel (Rust) + block syscalls
R6: Filesystem and package manager v0 (services; shell runs a packaged app)
Optional R7: VirtIO net in kernel (Rust) + net syscalls + UDP demo

G1: Go services bringup (Track A: TinyGo-first)
G2: Full Go port (Track B: long-term, optional until mature)

---

## M0: Boot + serial logging (asm + Rust entry)

### Definition of done
- Limine boots the kernel in QEMU.
- Serial output prints deterministic markers and exits cleanly via debug-exit.
- Panic path prints a deterministic marker and exits with failure.

### Issues
- [ ] (p0) Limine boot image skeleton (ISO builder, limine.conf)
- [ ] (p0) asm `_start` sets stack and calls Rust entry
- [ ] (p0) Rust kernel skeleton: `kmain()` prints markers
- [ ] (p0) `tools/run_qemu.sh` canonical runner
- [ ] (p0) CI: build + boot smoke test in headless QEMU

### Acceptance tests (marker-based)
- `tests/boot/test_boot_banner.py` expects:
  - `RUGO: boot ok`
  - `RUGO: halt ok`
- `tests/boot/test_panic_path.py` expects:
  - `RUGO: panic code=...`

---

## R1: Paging + traps + page fault reporting (Rust)

### Definition of done
- Paging enabled with known mapping strategy.
- IDT installed.
- Page fault handler logs fault address and error bits.

### Issues
- [ ] (p0) Parse Limine memory map, initialize physical allocator
- [ ] (p0) Build initial page tables and enable paging
- [ ] (p0) Install GDT and IDT
- [ ] (p0) Exception handlers: page fault, GPF, double fault
- [ ] (p1) Add debug symbols and helpers (nm, objdump, addr2line workflow)

### Acceptance tests
- `tests/boot/test_paging_enabled.py` expects:
  - `MM: paging=on`
- `tests/trap/test_page_fault_report.py` expects:
  - `PF: addr=0x... err=0x...`
- `tests/trap/test_idt_smoke.py` expects:
  - deterministic trap marker for a forced divide-by-zero or breakpoint

---

## R2: Scheduler + kernel threads (Rust)

### Definition of done
- Timer interrupts tick.
- At least two kernel threads can run and context switch.
- A minimal lock primitive exists and is safe with interrupts.

### Issues
- [ ] (p1) Timer source configured (PIT or APIC timer)
- [ ] (p1) Thread struct, runnable queue, context switch glue
- [ ] (p1) Preemption via timer tick, safe critical section rules
- [ ] (p1) Kernel test threads printing markers A and B

### Acceptance tests
- `tests/sched/test_timer_ticks.py` expects:
  - `TICK: 100`
- `tests/sched/test_two_threads.py` expects:
  - interleaved `A` and `B`

---

## R3: User mode + syscall ABI v0

### Definition of done
- Kernel can enter ring 3.
- Syscalls round-trip safely.
- User faults are contained and do not crash the kernel.

### Syscall ABI v0 (minimum)
- debug: `sys_debug_write`
- tasking: `sys_thread_spawn`, `sys_thread_exit`, `sys_yield`
- memory: `sys_vm_map`, `sys_vm_unmap`
- shm: `sys_shm_create`, `sys_shm_map`
- ipc: `sys_ipc_send`, `sys_ipc_recv`
- time: `sys_time_now`

### Issues
- [ ] (p1) User address space creation and mapping
- [ ] (p1) Syscall entry/exit path (asm stub, Rust dispatch)
- [ ] (p1) Minimal user runtime (start with freestanding C or Rust userland)
- [ ] (p1) Document syscall numbers and structs in `docs/abi/syscall_v0.md`
- [ ] (p1) User pointer validation strategy (copyin/copyout policy)

### Acceptance tests
- `tests/user/test_enter_user_mode.py` expects:
  - `USER: hello`
- `tests/user/test_syscall_roundtrip.py` expects:
  - `SYSCALL: ok`
- `tests/user/test_user_fault.py` expects:
  - `USER: killed` (or equivalent) and kernel continues running

---

## R4: IPC + shared memory + service registry v0

### Definition of done
- Two user processes can exchange messages through kernel IPC endpoints.
- Shared memory can be created and mapped by two processes.
- A service registry exists for name to endpoint resolution.

### Issues
- [ ] (p1) IPC endpoint object and queueing
- [ ] (p1) Blocking recv, wakeups
- [ ] (p1) Shared memory objects integrated with handle table
- [ ] (p2) Service registry: kernel table or svcman process (pick one and document)

### Acceptance tests
- `tests/ipc/test_ping_pong.py` expects:
  - `PING: ok` and `PONG: ok`
- `tests/ipc/test_shm_bulk.py` expects:
  - `SHM: checksum ok`

---

## R5: VirtIO block in kernel (Rust) + block syscalls

This is intentionally hybrid: drivers in kernel for early stability and speed, while high-level policy lives in user space.

### Definition of done
- VirtIO block works in QEMU.
- Kernel exposes block read/write syscalls (or a single block syscall).
- Read/write passes deterministic data integrity tests.

### Issues
- [ ] (p2) PCI discovery and VirtIO transport (MMIO or PCI)
- [ ] (p2) Virtqueue implementation and request submission
- [ ] (p2) Block read/write API and syscalls
- [ ] (p2) Disk image builder for tests

### Acceptance tests
- `tests/drivers/test_virtio_blk_identify.py` expects:
  - `BLK: found virtio-blk`
- `tests/drivers/test_virtio_blk_rw.py` expects:
  - `BLK: rw ok`

---

## R6: Filesystem + package manager + shell

### Definition of done
- A filesystem service exists that can open, read, write, list.
- A package tool can install a package and run an app.
- A shell can run a packaged hello app.

### Issues
- [ ] (p2) Filesystem format choice for v0 and documentation
- [ ] (p2) `fsd` protocol over IPC or syscalls (pick one, document)
- [ ] (p2) `pkg` package format v0: manifest + payload archive
- [ ] (p2) `sh` minimal shell: run, ls, cat, echo
- [ ] (p2) Integration image builder includes a sample package

### Acceptance tests
- `tests/fs/test_fsd_smoke.py` expects:
  - `FSD: mount ok`
- `tests/pkg/test_pkg_install_run.py` expects:
  - `APP: hello world`

---

## Optional R7: VirtIO net in kernel (Rust) + net syscalls + UDP demo

### Definition of done
- VirtIO net works in QEMU.
- Kernel exposes send and recv syscalls.
- A UDP echo demo passes.

### Issues
- [ ] (p3) VirtIO net driver in kernel
- [ ] (p3) Net syscalls: send/recv
- [ ] (p3) UDP echo demo app and QEMU networking setup

### Acceptance tests
- `tests/net/test_udp_echo.py` expects:
  - UDP echo marker

---

## G1: Go services bringup (Track A: TinyGo-first)

### Definition of done
- At least one user space service is written in Go and runs on your OS.
- The service uses the existing syscall ABI and IPC primitives (no new kernel features required).
- A test asserts a deterministic marker such as `GOUSR: ok`.

### Issues
- [ ] (p2) Define syscall and IPC bindings for Go (thin wrappers)
- [ ] (p2) Add a TinyGo target or build mode for your OS userland
- [ ] (p2) Implement one Go service (suggested: svcman client or IPC echo server)
- [ ] (p2) Add `tests/go/test_go_user_service.py`

### Acceptance tests
- `tests/go/test_go_user_service.py` expects:
  - `GOUSR: ok`

---

## G2: Full Go port (Track B: long-term)

This milestone is intentionally long-term. Treat it as optional until the OS stops churning.

### Start conditions (gate)
- Syscall ABI has been stable across multiple releases.
- Process/thread model is stable and documented.
- Filesystem and networking contracts are stable enough that the Go runtime can rely on them.

### Definition of done
- Standard Go toolchain can produce binaries for your GOOS/GOARCH.
- Go runtime syscalls and thread management work on your OS.
- A standard Go hello binary runs and prints a deterministic marker.

### Issues
- [ ] (p3) Choose GOOS name and define the runtime syscall surface needed
- [ ] (p3) Implement runtime glue (syscalls, threads, timers, signals or equivalents)
- [ ] (p3) Toolchain and linker integration (build and run standard Go binaries)
- [ ] (p3) Add `tests/go/test_std_go_binary.py`

### Acceptance tests
- `tests/go/test_std_go_binary.py` expects:
  - `GOSTD: ok`

---

## References (for implementers)
- Rust target `x86_64-unknown-none` platform support notes (no std; allocator required for alloc).
- Go porting policy (ports are OS/arch; avoid broken/incomplete ports).
- TinyGo documentation (targets; language and stdlib support notes).
