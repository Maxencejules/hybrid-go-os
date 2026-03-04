# Post-G2 Extended Milestones (Research Roadmap)

Date: 2026-03-04  
Status: Active (M8-M11 complete; M12 next)  
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

Milestone status: done (2026-03-04).

### Goal

Turn the G2 stock-Go bring-up path into a maintainer-grade, release-gated
`GOOS=rugo` port with reproducible toolchain outputs and a documented ABI
stability window.

### Current baseline (post-M10)

- G2 proves stock-Go artifact generation (`tools/build_go_std_spike.sh`,
  `tools/gostd_stock_builder/main.go`).
- Runtime bridge markers and contract metadata are test-backed
  (`tests/go/test_std_go_binary.py`, `docs/abi/go_port_spike_v0.md`).
- Compatibility, hardware, and security gates are already release-gated.
- Missing for M11 closure: runtime syscall/behavior coverage accounting,
  full bootstrap/rebuild workflow, a port qualification gate, and ABI stability
  policy docs.

### Implementation strategy

1. Freeze target and ABI contracts:
   - publish runtime-facing syscall contract and deprecation window policy.
   - declare required toolchain versions and deterministic build knobs.
2. Close runtime syscall and behavior gaps:
   - build a coverage matrix from runtime requirements.
   - implement or explicitly defer unsupported paths with deterministic behavior.
3. Build a reproducible bootstrap lane:
   - add a one-command setup/check flow for host and container environments.
   - emit machine-readable contract/reproducibility artifacts.
4. Add release-blocking qualification:
   - create an `all.bash`-style port qualification target.
   - gate CI on runtime stress and ABI-window checks.
5. Establish long-term ownership:
   - name maintainers and define breakage/deprecation workflow.

### Execution plan (3 PRs)

#### PR-1: Port Contract + Runtime Coverage Matrix

##### Objective

Define what the runtime port guarantees, then make all gaps explicit and
measurable.

##### Scope

- Add docs:
  - `docs/runtime/port_contract_v1.md`
  - `docs/runtime/syscall_coverage_matrix_v1.md`
  - `docs/runtime/abi_stability_policy_v1.md`
- Map runtime-required syscall/behavior surface against current kernel
  implementation.
- Add doc contract tests for completeness and format.
- Record unsupported features as explicit deferred items with owner/date.

##### Acceptance checks

- `python -m pytest tests/runtime/test_runtime_contract_docs_v1.py -v`
- `python -m pytest tests/go/test_std_go_binary.py -v`

##### Done criteria for PR-1

- Coverage matrix has no unowned TODO rows.
- ABI stability window and compatibility policy are versioned and reviewable.

#### PR-2: Bootstrap + Reproducibility Toolchain Lane

##### Objective

Make `GOOS=rugo` build/test setup reproducible across hosts and CI.

##### Scope

- Add bootstrap artifacts:
  - `tools/bootstrap_go_port_v1.sh`
  - `tools/runtime_toolchain_contract_v1.py`
  - optional reference container file (`tools/runtime_port.Dockerfile`).
- Emit deterministic contract/report artifacts:
  - `out/runtime-toolchain-contract.env`
  - `out/runtime-toolchain-repro.json`
- Document end-to-end setup and rebuild workflow:
  - `docs/runtime/toolchain_bootstrap_v1.md`

##### Acceptance checks

- `bash tools/bootstrap_go_port_v1.sh --check`
- `python tools/runtime_toolchain_contract_v1.py --out out/runtime-toolchain-contract.env`
- `python tools/runtime_toolchain_contract_v1.py --repro --out out/runtime-toolchain-repro.json`

##### Done criteria for PR-2

- A clean environment can reproduce expected artifacts with documented steps.
- Contract and repro artifacts are stable across two fresh runs.

#### PR-3: Qualification Gate + Milestone Closure

##### Objective

Create a release-blocking M11 gate and wire ownership/process requirements.

##### Scope

- Add runtime qualification target:
  - `make test-runtime-maturity`
- Add CI gate:
  - `.github/workflows/ci.yml` step `Runtime + toolchain maturity v1 gate`.
- Add runtime qualification tests:
  - `tests/runtime/test_runtime_stress_v1.py`
  - `tests/runtime/test_runtime_abi_window_v1.py`
- Record maintainers and breakage policy:
  - `docs/runtime/maintainers_v1.md`
- Wire status docs for milestone closure once gate is green.

##### Acceptance checks

- `make test-runtime-maturity`
- `python -m pytest tests/runtime -v`
- `python -m pytest tests/go/test_std_go_binary.py tests/compat/test_posix_subset.py -v`

##### Done criteria for PR-3

- Runtime maturity gate is mandatory in CI.
- Port ownership and deprecation workflow are documented.
- M11 is evidence-backed and ready to be marked `done`.

### Work packages

- M11.1 `GOOS=rugo` port contract v1 (`docs/runtime/port_contract_v1.md`).
- M11.2 runtime syscall/behavior coverage matrix + owned gap list.
- M11.3 bootstrap + reproducibility toolchain lane and artifacts.
- M11.4 `all.bash`-style qualification gate (`make test-runtime-maturity` + CI).
- M11.5 ABI stability + maintainership/deprecation policy docs.

### Exit criteria

- Runtime coverage matrix is complete; all open gaps are closed or explicitly
  deferred with owner/date.
- Toolchain bootstrap and reproducibility flow is documented, executable, and
  artifact-backed.
- Port has named maintainers and release-blocking CI gate.

### Acceptance tests (examples)

- Runtime stress tests (threads, timers, net IO, memory pressure) pass.
- Cross-version binary compatibility tests pass for frozen ABI window.
- Toolchain contract/repro artifacts match across clean rebuilds.

### Risks and non-goals

- Non-goals:
  - shipping full upstream-Go port acceptance in this milestone.
  - solving network/storage feature parity issues owned by M12/M13.
- Risks to track:
  - hidden runtime assumptions in unsupported syscall paths.
  - host toolchain drift causing false reproducibility failures.

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

1. Create `docs/M12_EXECUTION_BACKLOG.md` and split M12 into 3 PRs:
   - IPv4 + UDP/TCP baseline contract,
   - socket semantics + timer/retransmission engine,
   - interop/soak CI gate + milestone closure.
2. Extend the post-G2 dashboard with network maturity signals:
   - TCP/UDP reliability pass rate,
   - fault-injection recovery trend,
   - interop matrix trend.
3. Freeze M12 ownership:
   - one milestone owner,
   - one net-test owner,
   - one protocol-owner,
   - one doc owner.

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
