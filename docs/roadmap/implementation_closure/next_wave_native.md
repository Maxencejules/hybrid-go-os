# Next-Wave Native Driver Backlog Closure

`M53` and `M54` are already marked `done` in the flat milestone ledger, but
they are best read as contract and gate milestones rather than as literal
native-driver completion. This document states the higher bar.

## Completed Backlogs In Scope

| Backlog | Current class | Current repo reading | Literal implementation target | Still required |
|---|---|---|---|---|
| `M53 Native Driver Contract Expansion v1` | `Evidence-first` | The repo has native-driver, PCIe DMA, firmware-blob, and diagnostics contracts plus deterministic evidence generators. | The kernel has a real native-driver subsystem with probe, bind, DMA-safe memory, interrupt handling, firmware policy, and live diagnostics. | Add a driver core, PCI device discovery, BAR mapping, interrupt routing, DMA policy enforcement, firmware-loading hooks, and runtime-generated diagnostics emitted by actual drivers. |
| `M54 Native Storage Drivers v1` | `Evidence-first` | The repo has NVMe and AHCI contracts, support-matrix v7, block-flush docs, and synthetic qualification tests, but no visible NVMe or AHCI runtime path in the kernel. | The kernel discovers NVMe or AHCI controllers, performs identify and queue setup, reads and writes blocks, flushes data, handles reset or timeout paths, and exports that path through the existing block or fsync surface. | Implement actual NVMe or AHCI drivers, integrate them with block I/O syscalls and filesystem durability semantics, add reset and error recovery, and prove them on supported virtual or physical controllers. |

## Architecture That Should Exist Before Calling These Done

- A driver subsystem:
  - stable device registry
  - probe and bind lifecycle
  - driver-owned state with teardown paths
- PCI support beyond the current VirtIO assumptions:
  - BAR discovery and mapping
  - MSI, MSI-X, or legacy interrupt routing
  - DMA-safe buffer allocation and ownership rules
- Runtime diagnostics:
  - identify and capability dumps from live drivers
  - queue and reset counters
  - surfaced health state for the operator and test lanes
- Storage integration:
  - request queue abstraction rather than direct one-off block logic
  - flush, timeout, error, and recovery semantics
  - filesystem-visible durability propagation

## Recommended Implementation Order

1. Extract the current VirtIO block path from `kernel_rs/src/lib.rs` into a
   general block-driver abstraction.
2. Add a real PCI device and MMIO support layer that later drivers can reuse.
3. Implement one native storage path end to end, preferably NVMe first.
4. Reuse the same block interface for AHCI only after the queue, timeout, and
   reset model is stable.
5. Replace synthetic native-storage evidence with artifacts collected from the
   live driver on supported controllers.

Until that exists, `M53` and `M54` should be treated as backlog closure for
contracts and qualification scaffolding, not as proof that native drivers are
already implemented.
