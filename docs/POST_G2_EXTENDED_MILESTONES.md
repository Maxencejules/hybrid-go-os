# Post-G2 Extended Milestones (Research Roadmap)

Date: 2026-03-04  
Status: Proposed  
Scope: Rugo lane after G2 completion

---

## Why this document exists

M0-M7 and G1-G2 prove the kernel and Go-service direction. This roadmap answers:

1. What is still missing to approach Linux/Windows/macOS class capability.
2. How to implement those gaps with realistic sequencing.
3. What "done" looks like for each step.

This is a research-backed implementation plan, not just a feature wishlist.

---

## Summary of the 7 missing areas

1. Compatibility layer and app ecosystem.
2. Real hardware support breadth.
3. Security hardening and isolation.
4. Runtime and toolchain maturity.
5. Full networking stack maturity.
6. Filesystem and storage robustness.
7. Productization (updates, release, supply chain, operations).

---

## Milestone map (proposed)

| Milestone | Focus | Primary missing area |
|---|---|---|
| M8 | Compatibility Profile v1 | 1 |
| M9 | Hardware Enablement Matrix v1 | 2 |
| M10 | Security Baseline v1 | 3 |
| M11 | Runtime + Toolchain Maturity v1 | 4 |
| M12 | Network Stack v1 | 5 |
| M13 | Storage Reliability v1 | 6 |
| M14 | Productization + Release Engineering v1 | 7 |

Recommended sequencing: M8 -> M9 -> M10 -> M11 -> M12 -> M13 -> M14.

Reason: compatibility and hardware unlock real workloads; security/toolchain/network/storage make them reliable; productization makes them sustainable.

---

## M8 - Compatibility Profile v1

### Goal

Define and implement a stable user-space compatibility profile that can run meaningful third-party software, not just project demos.

### Implementation strategy

1. Freeze an ABI profile:
   - System call surface versioned as `syscall_v1`.
   - x86_64 SysV calling convention and ELF64 loader behavior documented.
2. Build a POSIX-first API target:
   - Start with high-value process, file, signal, time, socket, poll/epoll, futex primitives.
   - Track explicitly unsupported APIs.
3. Introduce compatibility tiers:
   - Tier A: native Rugo binaries.
   - Tier B: POSIX-oriented apps built against selected libc profile.
   - Tier C: optional Linux ABI shim (if adopted).
4. Add ecosystem bootstrap:
   - Minimal package format and repository metadata.
   - Base userland profile (shell, core tools, init/service manager).

### Work packages

- M8.1 ABI contract and test fixtures (`docs/abi/syscall_v1.md`, ABI tests).
- M8.2 ELF loader hardening (dynamic linking, relocations, aux vector policy).
- M8.3 libc target decision (`musl`-style compatibility profile or equivalent).
- M8.4 package manager and repository signing format v1.
- M8.5 compatibility CI lane (build-run matrix for canonical user-space apps).

### Exit criteria

- Versioned ABI document with no unresolved TODOs.
- At least one external app suite installs and runs from packages.
- Compatibility test suite reaches a fixed pass threshold and is release-gated.

### Acceptance tests (examples)

- Static and dynamic ELF binaries run with expected loader semantics.
- Process/thread/signal regression pack passes.
- File/socket API conformance pack passes for selected POSIX subset.

---

## M9 - Hardware Enablement Matrix v1

### Goal

Move from mostly QEMU-centric support to a maintainable, tiered hardware target matrix.

### Implementation strategy

1. Define hardware tiers:
   - Tier 0: QEMU reference platforms.
   - Tier 1: common x86_64 desktop/laptop virtual and bare-metal targets.
   - Tier 2: opportunistic/experimental.
2. Build a unified driver lifecycle:
   - Probe -> init -> runtime health -> teardown.
   - Standard IRQ, DMA, and MMIO patterns.
3. Expand device coverage deliberately:
   - Storage: NVMe/AHCI following virtio-blk maturity.
   - Network: additional NIC families beyond current baseline.
   - Input/timers/power needed for interactive system use.
4. Add hardware regression harness:
   - Boot and smoke tests per target class.
   - Device capability and fallback reporting in serial logs and artifacts.

### Work packages

- M9.1 `docs/hw/support_matrix_v1.md`.
- M9.2 PCI subsystem cleanup for multi-driver registration and resource arbitration.
- M9.3 DMA safety checks and IOMMU strategy draft.
- M9.4 ACPI and UEFI table handling hardening.
- M9.5 bare-metal bring-up runbook and diagnostics.

### Exit criteria

- Published and CI-enforced hardware matrix with pass/fail history.
- Deterministic boot + storage + network smoke on all Tier 0 and Tier 1 targets.
- Driver model conventions adopted across in-tree drivers.

### Acceptance tests (examples)

- Per-device probe/init markers and negative-path tests.
- Hotplug and reset path tests for supported devices.
- DMA boundary and invalid-mapping rejection tests.

---

## M10 - Security Baseline v1

### Goal

Establish enforceable least-privilege and secure-boot/update foundations.

### Implementation strategy

1. Adopt explicit rights model:
   - Per-handle/per-object rights with reduction and transfer semantics.
2. Tighten memory and execution protections:
   - W^X discipline, executable mapping policy, kernel/user separation checks.
3. Introduce sandboxing primitives:
   - Per-process syscall and resource policy (seccomp/landlock-like direction).
4. Build trusted boot chain:
   - Signed boot artifacts, measured boot/attestation-ready metadata.
5. Add continuous vulnerability discovery:
   - Coverage-enabled syscall fuzzing.
   - Security regression packs as release gates.

### Work packages

- M10.1 rights and capability model doc + kernel enforcement.
- M10.2 secure boot policy and key rotation procedure.
- M10.3 syscall filtering framework and default profiles.
- M10.4 kernel fuzz harness integration (coverage + crash triage loop).
- M10.5 incident response and security advisory process.

### Exit criteria

- Rights model enforced by default for user-space resource access.
- Boot path validates signed artifacts.
- Fuzzing runs continuously with tracked crash SLA and fix workflow.

### Acceptance tests (examples)

- Unauthorized operations denied with deterministic errors.
- Tampered boot artifacts rejected.
- Sandbox profiles prevent forbidden syscalls and paths.

---

## M11 - Runtime and Toolchain Maturity v1

### Goal

Turn the current G2 baseline into a maintainer-grade runtime/toolchain port.

### Implementation strategy

1. Formalize target contract:
   - Target triple, compiler flags, linker and relocation policy.
2. Complete language runtime integration:
   - Scheduler, timers, memory primitives, signals, netpoll hooks.
3. Build reproducible toolchain lane:
   - Pinned compilers, deterministic artifacts, bootstrap docs.
4. Add port maintenance process:
   - Port owners, CI builders, breakage policy, deprecation policy.

### Work packages

- M11.1 native `GOOS=rugo` full-port plan (beyond marker binary path).
- M11.2 runtime syscall coverage matrix and gap closure.
- M11.3 toolchain bootstrap scripts and reference container image.
- M11.4 port qualification pipeline (`all.bash`-style equivalent + integration suite).
- M11.5 ABI stability policy for runtime-facing syscalls.

### Exit criteria

- Full runtime conformance suite for chosen language targets passes in CI.
- Toolchain builds are reproducible and documented end-to-end.
- Port has named maintainers and release-blocking CI.

### Acceptance tests (examples)

- Runtime stress tests (threads, timers, net IO, memory pressure) pass.
- Cross-version binary compatibility tests pass for frozen ABI window.

---

## M12 - Network Stack v1

### Goal

Move from UDP-echo milestone coverage to production-oriented network behavior.

### Implementation strategy

1. Stabilize L2/L3 fundamentals:
   - ARP/ND, ICMP/ICMPv6, routing table and neighbor cache behavior.
2. Implement robust transport:
   - UDP hardening and full TCP state machine correctness.
   - Retransmission, congestion control baseline, timer correctness.
3. Establish socket contract:
   - Blocking/non-blocking semantics, poll/epoll integration, error model.
4. Add user-space network services:
   - DNS resolver path, TLS-ready client/server workflows.

### Work packages

- M12.1 IPv4 baseline compliance pass.
- M12.2 TCP state/timer engine with packet-level traces.
- M12.3 IPv6 baseline (addressing, neighbor discovery, ICMPv6 essentials).
- M12.4 network soak and fault-injection tests (loss, reorder, duplication).
- M12.5 interop matrix with Linux/BSD peers.

### Exit criteria

- Deterministic TCP/UDP integration suite passes.
- Long-running soak tests meet reliability and throughput targets.
- Socket API behavior is documented and regression-gated.

### Acceptance tests (examples)

- RFC-aligned transport conformance vectors.
- DNS + HTTPS client flow succeeds in clean and degraded links.
- Connection churn and retransmission stress tests pass.

---

## M13 - Storage Reliability v1

### Goal

Evolve from functional FS behavior to crash-consistent, recoverable storage.

### Implementation strategy

1. Define storage correctness model:
   - Metadata consistency, data durability classes, fsync semantics.
2. Choose and implement reliability strategy:
   - Journaling or copy-on-write model with explicit recovery guarantees.
3. Add integrity and recovery tooling:
   - Checksums, replay, scrub/fsck-like validation utilities.
4. Test failure realism:
   - Power-loss and abrupt-reset campaigns integrated in CI.

### Work packages

- M13.1 FS v1 spec (`docs/storage/fs_v1.md`) with crash model.
- M13.2 write ordering, barriers, and flush policy.
- M13.3 replay/recovery utility and offline verifier.
- M13.4 snapshot/rollback strategy (if CoW selected).
- M13.5 storage endurance and corruption-injection suite.

### Exit criteria

- Crash-consistency claims documented and empirically validated.
- Recovery tools restore a clean mountable state across fault campaigns.
- Durability behavior is predictable and test-backed.

### Acceptance tests (examples)

- Repeated forced power cuts during metadata/data updates.
- Post-recovery integrity scans and workload replay checks.
- Large-file, many-file, and metadata-heavy stress runs.

---

## M14 - Productization and Release Engineering v1

### Goal

Make the OS operable as a real product: installable, updatable, auditable, and supportable.

### Implementation strategy

1. Define release train:
   - Stable, beta, nightly channels; LTS policy; backport workflow.
2. Secure update pipeline:
   - Signed metadata and target files, rollback protection, key rotation.
3. Supply-chain security and transparency:
   - Build provenance, SBOM generation, artifact attestations.
4. Reproducibility and observability:
   - Deterministic release images and standardized crash/telemetry data.
5. Operational UX:
   - Installer, recovery mode, system diagnostics and support bundle tools.

### Work packages

- M14.1 release policy and versioning scheme.
- M14.2 OTA/update client and repository service.
- M14.3 provenance + SBOM emission in CI.
- M14.4 reproducible build gate (hash equality across clean environments).
- M14.5 installer and recovery UX baseline.

### Exit criteria

- Signed OTA updates with rollback/expiry protections in production flow.
- Every release has SBOM + provenance artifacts.
- Reproducibility checks are mandatory release gates.

### Acceptance tests (examples)

- Update attack simulations (replay, freeze, key compromise drills).
- Fresh install + upgrade + rollback end-to-end tests.
- Multi-run reproducibility checks for release artifacts.

---

## Cross-cutting governance (applies to M8-M14)

1. Every milestone has:
   - design doc,
   - threat model update,
   - CI lane,
   - rollback plan.
2. No milestone is marked done without:
   - at least one negative-path test suite,
   - performance baseline capture,
   - release note with known limitations.
3. Keep milestone cadence fixed:
   - target 8-12 weeks per milestone,
   - avoid parallelizing more than two high-risk milestones at once.

---

## Suggested immediate next actions

1. Create `M8` design doc and split into 4 implementation PRs:
   - ABI contract,
   - loader and process primitives,
   - libc compatibility profile,
   - package/repo bootstrap.
2. Start a "post-G2 CI" dashboard with:
   - compatibility,
   - hardware matrix,
   - security fuzzing,
   - reproducibility checks.
3. Freeze ownership:
   - one milestone owner,
   - one test owner,
   - one doc owner per milestone.

---

## Research references (primary sources)

Compatibility and ABI:
- POSIX Issue 8 (Open Group online publications): https://pubs.opengroup.org/onlinepubs/9799919799/
- POSIX Issue 8 download index: https://pubs.opengroup.org/onlinepubs/9799919799/download/index.html
- FreeBSD Linux Binary Compatibility chapter: https://docs.freebsd.org/en/books/handbook/linuxemu/
- NetBSD binary emulation overview: https://www.netbsd.org/Documentation/compat.html
- QEMU user-mode emulation: https://www.qemu.org/docs/master/user/main.html

Hardware and platform:
- Virtio 1.2 spec: https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html
- Linux PCI driver model guide: https://www.kernel.org/doc/html/next/PCI/pci.html
- UEFI 2.10 spec: https://uefi.org/specs/UEFI/2.10/
- ACPI 6.5 spec: https://uefi.org/specs/ACPI/6.5/index.html

Security:
- NIST SP 800-193 (platform firmware resiliency): https://csrc.nist.gov/pubs/sp/800/193/final
- NIST SP 800-218 (SSDF): https://csrc.nist.gov/publications/detail/sp/800-218/final
- secL4 capabilities tutorial: https://docs.sel4.systems/Tutorials/capabilities.html
- seL4 white paper: https://sel4.systems/About/whitepaper.html
- Linux seccomp filter docs: https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html
- Linux Landlock docs: https://www.kernel.org/doc/html/latest/userspace-api/landlock.html
- syzkaller project: https://github.com/google/syzkaller
- KCOV docs: https://docs.kernel.org/next/dev-tools/kcov.html

Runtime and toolchain:
- Go porting policy: https://go.dev/wiki/PortingPolicy
- Go minimum requirements: https://go.dev/wiki/MinimumRequirements
- musl project overview: https://musl.libc.org/

Networking:
- TCP (RFC 9293): https://www.rfc-editor.org/info/rfc9293
- Host requirements (RFC 1122): https://www.rfc-editor.org/info/rfc1122
- UDP (RFC 768): https://www.rfc-editor.org/info/rfc768
- IPv4 (RFC 791): https://www.rfc-editor.org/info/rfc791
- ARP (RFC 826): https://www.rfc-editor.org/info/rfc826
- IPv6 (RFC 8200): https://www.rfc-editor.org/info/rfc8200
- IPv6 Neighbor Discovery (RFC 4861): https://www.rfc-editor.org/info/rfc4861

Filesystem and storage:
- ext4 journal design (jbd2): https://docs.kernel.org/filesystems/ext4/journal.html
- ext4 admin behavior notes: https://www.kernel.org/doc/html/latest/admin-guide/ext4.html
- btrfs docs: https://docs.kernel.org/filesystems/btrfs.html
- Linux VFS overview: https://docs.kernel.org/filesystems/vfs.html

Productization and supply chain:
- TUF specification: https://theupdateframework.github.io/specification/
- SLSA spec v1.2: https://slsa.dev/spec/v1.2/
- SPDX specification 3.0.1: https://spdx.github.io/spdx-spec/v3.0.1/
- SOURCE_DATE_EPOCH specification: https://reproducible-builds.org/specs/source-date-epoch/

