# Post-G2 Extended Milestones (Research Roadmap)

Date: 2026-03-04  
Status: Complete (M8-M14 complete)  
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

Milestone status: done (2026-03-04).

### Goal

Turn the M7 UDP-echo baseline into a maintainer-grade, release-gated network
lane with explicit socket semantics, TCP correctness, and interop/soak
evidence.

### Current baseline (post-M11)

- M7 provides a kernel-side VirtIO-net polling path with ARP + IPv4 UDP echo
  coverage (`tests/net/test_udp_echo.py`, `docs/net/udp_echo_v0.md`).
- ABI v1 already reserves raw frame networking via `sys_net_send` and
  `sys_net_recv` (`docs/abi/syscall_v1.md`), but no network v1 socket contract
  is published yet.
- QEMU fixtures already support deterministic UDP inject and tiered net-machine
  profiles (`tests/conftest.py`: `_boot_iso_with_net`, `qemu_serial_net_*`).
- M9 hardware matrix proves basic net probe/init across tiered machine profiles.
- Kickoff gaps (closed in M12): versioned network contracts, TCP state/timer
  correctness coverage, IPv6 baseline docs/tests, and a dedicated network CI
  maturity gate.

### Implementation strategy

1. Freeze network contracts and observability:
   - Publish versioned L2/L3/L4/socket docs with deterministic error behavior.
   - Define serial/trace artifacts for repeatable network triage.
2. Raise transport correctness:
   - Keep UDP behavior deterministic under load/loss.
   - Add TCP state machine baseline with retransmission/timer rules.
3. Lock socket semantics:
   - Define blocking/non-blocking and poll integration behavior.
   - Document unsupported operations explicitly as deterministic failures.
4. Add IPv6 baseline:
   - Addressing, ICMPv6 essentials, and neighbor discovery baseline.
5. Promote reliability to release gates:
   - Add interop and soak/fault-injection lanes with artifact outputs.

### Execution plan (3 PRs)

#### PR-1: Contract Freeze + IPv4/UDP Baseline Gate

##### Objective

Make current IPv4/UDP behavior explicit and test-gated before adding TCP/IPv6
complexity.

##### Scope

- Add docs:
  - `docs/net/network_stack_contract_v1.md`
  - `docs/net/socket_contract_v1.md`
  - `docs/net/ipv4_udp_profile_v1.md`
- Add/extend executable checks:
  - `tests/net/test_udp_echo.py` (positive + deterministic negative paths)
  - `tests/net/test_ipv4_udp_contract_v1.py`
  - `tests/net/test_socket_contract_docs_v1.py`
- Add optional trace/report helper:
  - `tools/net_trace_capture_v1.py`

##### Acceptance checks

- `python -m pytest tests/net/test_udp_echo.py tests/net/test_ipv4_udp_contract_v1.py -v`
- `python -m pytest tests/net/test_socket_contract_docs_v1.py -v`

##### Done criteria for PR-1

- Network v1 contract docs are versioned and test-referenced.
- IPv4/UDP behavior (including failure paths) is deterministic and executable.

#### PR-2: TCP State/Timer Engine + Socket Semantics

##### Objective

Implement a deterministic TCP baseline and bind it to explicit socket behavior
contracts.

##### Scope

- Add TCP baseline behavior:
  - handshake, established data flow, close/teardown, reset handling.
  - retransmission and timer policy with deterministic retry/fail semantics.
- Add tests:
  - `tests/net/test_tcp_state_machine_v1.py`
  - `tests/net/test_tcp_retransmission_v1.py`
  - `tests/net/test_socket_poll_semantics_v1.py`
- Add docs:
  - `docs/net/tcp_state_machine_v1.md`
  - `docs/net/retransmission_timer_policy_v1.md`

##### Acceptance checks

- `python -m pytest tests/net/test_tcp_state_machine_v1.py tests/net/test_tcp_retransmission_v1.py -v`
- `python -m pytest tests/net/test_socket_poll_semantics_v1.py -v`

##### Done criteria for PR-2

- TCP lifecycle and timer/retransmission behavior are deterministic and
  test-backed.
- Socket poll/blocking semantics are documented and enforced by tests.

#### PR-3: IPv6 Baseline + Interop/Soak Gate + Milestone Closure

##### Objective

Close M12 with IPv6 baseline behavior and mandatory network maturity gates in
local and CI lanes.

##### Scope

- Add IPv6 baseline docs/tests:
  - `docs/net/ipv6_baseline_v1.md`
  - `tests/net/test_ipv6_nd_icmpv6_v1.py`
- Add interop/soak tooling and checks:
  - `tools/run_net_interop_matrix_v1.py`
  - `tools/run_net_soak_v1.py`
  - `tests/net/test_net_interop_matrix_v1.py`
  - `tests/net/test_net_soak_v1.py`
- Add release gates:
  - `Makefile` target `test-network-stack-v1`
  - `.github/workflows/ci.yml` step `Network stack v1 gate`
- Mark milestone/status docs once gate is green.

##### Acceptance checks

- `make test-network-stack-v1`
- `python -m pytest tests/net -v`
- `python tools/run_net_interop_matrix_v1.py --out out/net-interop-v1.json`
- `python tools/run_net_soak_v1.py --out out/net-soak-v1.json`

##### Done criteria for PR-3

- Network maturity gate is mandatory in CI.
- IPv4/UDP/TCP/IPv6 baseline behavior has interop + soak evidence artifacts.
- M12 is evidence-backed and marked `done` in milestone/status docs.

### Work packages

- M12.1 network stack contract docs v1 (IPv4/UDP/TCP/socket semantics).
- M12.2 TCP state/timer and retransmission engine with traceability artifacts.
- M12.3 IPv6 baseline (addressing, ND, ICMPv6 essentials) and contract tests.
- M12.4 network soak/fault-injection harness and machine-readable reports.
- M12.5 interop matrix + release-blocking local/CI network maturity gate.

### Exit criteria

- Socket/network contracts are versioned, executable, and release-gated.
- Deterministic TCP/UDP suites pass under clean and degraded link conditions.
- Interop + soak lanes produce stable reports and satisfy target thresholds.

### Acceptance tests (examples)

- RFC-aligned UDP/TCP conformance vectors (including failure paths).
- DNS + HTTPS client flow succeeds under clean and degraded links.
- Connection churn and retransmission stress suites pass.

### Risks and non-goals

- Non-goals:
  - full Linux socket API parity in M12.
  - advanced congestion-control variants beyond a baseline policy.
  - full routing/firewall/NAT feature set in this milestone.
- Risks to track:
  - QEMU user-net behavior may hide physical-wire edge cases.
  - timer granularity drift may destabilize retransmission determinism.
  - interop flakiness without pinned peer versions/configs.

---

## M13 - Storage Reliability v1

Milestone status: done (2026-03-04).

### Goal

Turn the current functional `SimpleFS v0` path into a crash-consistent,
recoverable, and release-gated storage reliability lane with explicit
durability semantics.

### Current baseline (post-M12)

- M6 delivers functional filesystem behavior with deterministic mount and app
  package flow (`tests/fs/test_fsd_smoke.py`, `tests/pkg/test_pkg_install_run.py`).
- On-disk format is documented as `SimpleFS v0` (`docs/storage/fs_v0.md`) and
  built deterministically by `tools/mkfs.py`.
- Basic invalid-superblock rejection exists (`tests/fs/test_fsd_bad_magic.py`).
- M5/M9 already provide deterministic VirtIO block probe/read/write baselines.
- Kickoff gaps (closed in M13): crash model and durability contract,
  write-ordering guarantees, replay/recovery tooling,
  corruption/power-loss campaigns, and a dedicated storage reliability CI gate.

### Implementation strategy

1. Freeze storage correctness contracts first:
   - define v1 crash model, durability classes, and `fsync`/flush guarantees.
   - document deterministic failure-path behavior for partial/aborted writes.
2. Implement recovery-capable write path:
   - choose reliability strategy (journaled metadata path or equivalent).
   - enforce write ordering and barrier policy in block-facing storage path.
3. Add verification and repair tooling:
   - replay/recovery utility, integrity checks, and offline verifier workflow.
4. Build realistic fault campaigns:
   - model repeated power-loss/reset points and corruption injection.
5. Promote reliability to release gates:
   - storage fault/recovery reports as mandatory local/CI evidence.

### Execution plan (3 PRs)

#### PR-1: Storage Contract Freeze + Crash Model Baseline

##### Objective

Define storage v1 guarantees and make durability semantics executable before
recovery implementation lands.

##### Scope

- Add docs:
  - `docs/storage/fs_v1.md`
  - `docs/storage/durability_model_v1.md`
  - `docs/storage/write_ordering_policy_v1.md`
- Add/extend executable checks:
  - `tests/storage/test_storage_contract_docs_v1.py`
  - `tests/storage/test_fsync_semantics_v1.py`
  - `tests/storage/test_write_ordering_contract_v1.py`
- Record explicit deferred items with owner/target date where needed.

##### Acceptance checks

- `python -m pytest tests/storage/test_storage_contract_docs_v1.py -v`
- `python -m pytest tests/storage/test_fsync_semantics_v1.py tests/storage/test_write_ordering_contract_v1.py -v`

##### Done criteria for PR-1

- Storage v1 contracts are versioned, reviewable, and test-referenced.
- Crash/durability semantics have no unowned placeholder rows.

#### PR-2: Replay/Recovery Tooling + Fault-Campaign Harness

##### Objective

Implement and validate deterministic recovery behavior under corruption and
power-loss scenarios.

##### Scope

- Add tooling:
  - `tools/storage_recover_v1.py`
  - `tools/run_storage_fault_campaign_v1.py`
- Add tests:
  - `tests/storage/test_storage_recovery_v1.py`
  - `tests/storage/test_storage_fault_campaign_v1.py`
  - `tests/storage/test_storage_integrity_checker_v1.py`
- Add docs:
  - `docs/storage/recovery_playbook_v1.md`
  - `docs/storage/fault_campaign_v1.md`

##### Acceptance checks

- `python tools/storage_recover_v1.py --check --out out/storage-recovery-v1.json`
- `python tools/run_storage_fault_campaign_v1.py --seed 20260304 --out out/storage-fault-campaign-v1.json`
- `python -m pytest tests/storage/test_storage_recovery_v1.py tests/storage/test_storage_fault_campaign_v1.py -v`

##### Done criteria for PR-2

- Recovery and fault-campaign tooling emits stable machine-readable artifacts.
- Corruption/power-loss scenarios produce deterministic pass/fail outcomes.

#### PR-3: Storage Reliability Gate + Milestone Closure

##### Objective

Close M13 with release-blocking storage reliability gates and evidence-linked
status closure.

##### Scope

- Add local gate:
  - `Makefile` target `test-storage-reliability-v1`
- Add CI gate:
  - `.github/workflows/ci.yml` step `Storage reliability v1 gate`
- Add aggregate storage test lane:
  - `tests/storage/test_storage_reliability_gate_v1.py`
- Wire artifact uploads:
  - `out/storage-recovery-v1.json`
  - `out/storage-fault-campaign-v1.json`
- Mark milestone/status docs once gate is green.

##### Acceptance checks

- `make test-storage-reliability-v1`
- `python -m pytest tests/storage -v`
- `python tools/storage_recover_v1.py --check --out out/storage-recovery-v1.json`
- `python tools/run_storage_fault_campaign_v1.py --seed 20260304 --out out/storage-fault-campaign-v1.json`

##### Done criteria for PR-3

- Storage reliability gate is mandatory in CI.
- Recovery/fault artifacts are stable and linked in milestone evidence.
- M13 is ready to be marked `done` in milestone/status docs.

### Work packages

- M13.1 storage v1 contracts (crash model, durability classes, fsync semantics).
- M13.2 write-ordering/barrier policy with deterministic failure behavior.
- M13.3 replay/recovery tooling + offline integrity verifier.
- M13.4 power-loss/corruption fault-campaign harness + artifact schema.
- M13.5 release-blocking local/CI storage reliability gate.

### Exit criteria

- Crash-consistency and durability claims are versioned, explicit, and tested.
- Recovery tooling restores a clean mountable state across campaign scenarios.
- Storage reliability artifacts are generated and enforced by release gates.

### Acceptance tests (examples)

- Repeated forced power cuts during metadata/data update phases.
- Post-recovery integrity/replay checks on clean and corrupted images.
- Mixed workload stress (large-file, many-file, metadata-heavy) with bounded
  failure thresholds.

### Risks and non-goals

- Non-goals:
  - full production filesystem feature parity (quotas, snapshots, online resize).
  - complete CoW snapshot/rollback system in M13 unless explicitly selected.
  - broad storage hardware family expansion beyond current virtio baseline.
- Risks to track:
  - hidden ordering assumptions between FS metadata and block flush behavior.
  - long fault campaigns increasing CI flakiness/runtime.
  - recovery correctness gaps that only appear under repeated power cuts.

---

## M14 - Productization and Release Engineering v1

Milestone status: done (2026-03-04).

### Goal

Turn the current milestone-complete platform into a shippable, supportable
product lane with versioned releases, signed updates, supply-chain evidence,
and installer/recovery baselines enforced by release gates.

### Current baseline (post-M13)

- M8-M13 are complete with release-blocking gates for compatibility, hardware,
  security, runtime/toolchain, network, and storage.
- Build determinism already exists at image level (`make repro-check`,
  `tools/mkimage.sh`, `docs/BUILD.md`).
- Security baseline already includes signed boot-manifest and key-rotation
  policy artifacts (`tools/secure_boot_manifest_v1.py`,
  `docs/security/secure_boot_policy_v1.md`).
- M11/M12/M13 already established the machine-readable artifact pattern in
  `out/*.json` and CI artifact uploads (`.github/workflows/ci.yml`).
- Kickoff gaps for M14: no release-channel contract, no signed OTA/update
  repository/client workflow, no SBOM/provenance release artifacts, no
  installer/recovery operation contract, and no dedicated release-engineering
  gate.

### Implementation strategy

1. Freeze release governance and channel contracts first:
   - stable/beta/nightly semantics, support windows, backport policy, and
     ownership/approval flow.
2. Build a signed update path with explicit rollback defenses:
   - signed metadata/targets, monotonic version policy, key-rotation workflow,
     and offline verification behavior.
3. Add supply-chain evidence to every releasable artifact:
   - SBOM output, provenance attestations, and artifact manifest checksums.
4. Promote reproducibility + release assembly to mandatory gates:
   - deterministic release-image checks and policy validation in local/CI.
5. Define operator-facing product UX baseline:
   - installer flow, recovery mode, and support bundle collection contract.

### Execution plan (3 PRs)

#### PR-1: Release Contract Freeze + Channel Governance

##### Objective

Make release/versioning policy executable before update transport mechanics are
implemented.

##### Scope

- Add release contract docs:
  - `docs/build/release_policy_v1.md`
  - `docs/build/versioning_scheme_v1.md`
  - `docs/build/release_checklist_v1.md`
- Add contract/report helper:
  - `tools/release_contract_v1.py`
- Add executable checks:
  - `tests/build/test_release_contract_docs_v1.py`
  - `tests/build/test_release_contract_report_v1.py`
- Freeze release-role ownership and escalation paths in docs.

##### Acceptance checks

- `python tools/release_contract_v1.py --out out/release-contract-v1.json`
- `python -m pytest tests/build/test_release_contract_docs_v1.py tests/build/test_release_contract_report_v1.py -v`

##### Done criteria for PR-1

- Release policy is versioned, reviewable, and test-referenced.
- Channel/support/backport rules have no unowned placeholders.
- Release contract report schema is stable.

#### PR-2: Signed Update Pipeline + Rollback Protection

##### Objective

Ship a deterministic, attack-aware OTA/update baseline with explicit replay,
freeze, and rollback defenses.

##### Scope

- Add update protocol docs:
  - `docs/pkg/update_protocol_v1.md`
  - `docs/pkg/update_repo_layout_v1.md`
  - `docs/security/update_signing_policy_v1.md`
- Add update tooling:
  - `tools/update_repo_sign_v1.py`
  - `tools/update_client_verify_v1.py`
  - `tools/run_update_attack_suite_v1.py`
- Add executable checks:
  - `tests/pkg/test_update_metadata_v1.py`
  - `tests/pkg/test_update_rollback_protection_v1.py`
  - `tests/pkg/test_update_attack_suite_v1.py`

##### Acceptance checks

- `python tools/update_repo_sign_v1.py --repo out/update-repo-v1 --out out/update-metadata-v1.json`
- `python tools/update_client_verify_v1.py --repo out/update-repo-v1 --expect-version 1.0.0`
- `python tools/run_update_attack_suite_v1.py --seed 20260304 --out out/update-attack-suite-v1.json`
- `python -m pytest tests/pkg/test_update_metadata_v1.py tests/pkg/test_update_rollback_protection_v1.py tests/pkg/test_update_attack_suite_v1.py -v`

##### Done criteria for PR-2

- Update metadata/targets are signed and verifiable with documented key-rotation
  behavior.
- Replay/freeze/rollback attack simulations have deterministic pass/fail
  outcomes.
- Update reports are machine-readable and schema-validated.

#### PR-3: Supply-Chain + Reproducibility Gate + Installer/Recovery Closure

##### Objective

Close M14 with release-blocking productization gates and evidence-linked
milestone closure.

##### Scope

- Add supply-chain docs/tooling:
  - `docs/build/supply_chain_policy_v1.md`
  - `tools/generate_sbom_v1.py`
  - `tools/generate_provenance_v1.py`
- Add installer/recovery baseline docs/tooling:
  - `docs/build/installer_recovery_baseline_v1.md`
  - `tools/collect_support_bundle_v1.py`
- Add release gate wiring:
  - `Makefile` target `test-release-engineering-v1`
  - `.github/workflows/ci.yml` step `Release engineering v1 gate`
- Add aggregate checks:
  - `tests/build/test_release_engineering_gate_v1.py`
- Wire release artifacts:
  - `out/release-contract-v1.json`
  - `out/update-attack-suite-v1.json`
  - `out/sbom-v1.spdx.json`
  - `out/provenance-v1.json`
- Mark milestone/status docs once gate is green.

##### Acceptance checks

- `make test-release-engineering-v1`
- `make repro-check`
- `python tools/generate_sbom_v1.py --out out/sbom-v1.spdx.json`
- `python tools/generate_provenance_v1.py --out out/provenance-v1.json`
- `python -m pytest tests/build/test_release_engineering_gate_v1.py -v`

##### Done criteria for PR-3

- Release-engineering gate is mandatory in local and CI lanes.
- Release artifacts include reproducibility, update-security, SBOM, and
  provenance evidence.
- M14 is evidence-backed and ready to be marked `done` in milestone/status docs.

### Work packages

- M14.1 release policy and versioning scheme.
- M14.2 signed OTA/update repository + client verification path.
- M14.3 provenance + SBOM artifact emission and schema validation in CI.
- M14.4 release-blocking reproducible build and release-assembly gate.
- M14.5 installer, recovery, and support-bundle operational baseline.

### Exit criteria

- Release/channel policy is versioned, executable, and owner-closed.
- Signed OTA/update flow enforces rollback/replay/freeze defenses.
- Every release candidate emits reproducibility + SBOM + provenance artifacts.
- Release engineering gate is mandatory for local and CI release lanes.

### Acceptance tests (examples)

- Update attack simulations (replay, freeze, rollback, key-rotation drills).
- Fresh install + upgrade + rollback + recovery mode end-to-end flow.
- Multi-run release-image reproducibility and artifact checksum verification.
- Support-bundle generation and redaction policy checks.

### Risks and non-goals

- Non-goals:
  - full enterprise fleet-management platform in M14.
  - complete package ecosystem governance beyond baseline update/release policy.
  - broad hardware-specific installer UX permutations beyond current QEMU/virtio
    baseline.
- Risks to track:
  - update signing key lifecycle mistakes causing lockout or unsafe bypass paths.
  - reproducibility drift from host/toolchain variance outside pinned baseline.
  - CI runtime growth from combined reproducibility + security + artifact gates.
  - installer/recovery flows diverging from documented operator procedures.

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

1. Keep the release-engineering gate green and trendable:
   - reproducibility pass rate,
   - update attack-suite pass rate,
   - SBOM/provenance artifact completeness.
2. Extend the post-G2 dashboard with productization signals:
   - OTA success and rollback trend,
   - SBOM/provenance coverage,
   - release reproducibility pass rate.
3. Freeze steady-state ownership:
   - one milestone owner,
   - one release-owner,
   - one update-pipeline owner,
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
