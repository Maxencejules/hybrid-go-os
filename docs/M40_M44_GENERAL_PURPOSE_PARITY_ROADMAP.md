# M40-M44 General-Purpose Parity Roadmap (Post-M39)

Date: 2026-03-09  
Lane: Rugo (Rust kernel + Go user space)  
Status: Proposed

## Why this document exists

M35-M39 closed the immediate expansion backlog, but major parity blockers remain
for "general-purpose OS" expectations:

1. Deferred compatibility surfaces (`fork`, `clone`, `epoll`, namespace/cgroup,
   `AF_NETLINK`, raw packet parity).
2. Desktop/hardware/ecosystem claims remain intentionally bounded by profile.
3. Several late-phase gates rely on deterministic model artifacts instead of
   runtime-collected evidence from real executions.

This roadmap defines the next execution phase to close those blockers without
making premature Linux/Windows parity claims.

## Scope and boundaries

In scope:
- Start M40-M44 as the next execution phase.
- Preserve contract-first delivery and machine-verifiable release gates.
- Convert compatibility and ecosystem claims to runtime-backed evidence.

Out of scope:
- Declaring universal app or hardware parity in one phase.
- Removing deterministic unsupported behavior for still-deferred surfaces.

## Sequencing map

| Milestone | Focus | Primary gate |
|---|---|---|
| M40 | Runtime-Backed Evidence Integrity v1 | `test-evidence-integrity-v1` |
| M41 | Process + Readiness Compatibility Closure v1 | `test-process-readiness-parity-v1` |
| M42 | Isolation + Namespace Baseline v1 | `test-isolation-baseline-v1` |
| M43 | Hardware/Firmware Breadth + SMP v1 | `test-hw-firmware-smp-v1` |
| M44 | Real Desktop + Ecosystem Qualification v2 | `test-real-ecosystem-desktop-v2` |

### Cross-cutting sub-gates (required)

| Sub-gate | Anchored milestone | Focus |
|---|---|---|
| `test-synthetic-evidence-ban-v1` | M40 | ban synthetic-only artifacts in release gates |
| `test-posix-gap-closure-v2` | M41 | close high-impact POSIX/runtime gaps with runtime evidence |
| `test-namespace-cgroup-v1` | M42 | deterministic containment and resource-control baseline |
| `test-native-driver-matrix-v1` | M43 | native AHCI/NVMe/NIC and firmware/SMP coverage |
| `test-real-app-catalog-v2` | M44 | real package/install/GUI workload qualification |

## Suggested cadence

- Planning cadence: 1 milestone per 8-12 weeks.
- PR pattern per milestone:
  - PR-1: contract freeze,
  - PR-2: implementation and tooling,
  - PR-3: release-gate wiring and closure.

## M40: Runtime-Backed Evidence Integrity v1

### Objective

Replace synthetic-only gate evidence with runtime-collected artifacts tied to
QEMU and bare-metal execution traces.

### PR-1 (contract freeze)

- Docs:
  - `docs/runtime/evidence_integrity_policy_v1.md`
  - `docs/runtime/runtime_evidence_schema_v1.md`
  - `docs/runtime/gate_provenance_policy_v1.md`
- Tests:
  - `tests/runtime/test_evidence_integrity_docs_v1.py`

### PR-2 (implementation + deterministic collection)

- Tooling:
  - `tools/collect_runtime_evidence_v1.py`
  - `tools/audit_gate_evidence_v1.py`
- Tests:
  - `tests/runtime/test_runtime_evidence_collection_v1.py`
  - `tests/runtime/test_gate_evidence_audit_v1.py`

### PR-3 (gate + closure)

- Gates:
  - `test-evidence-integrity-v1`
  - sub-gate `test-synthetic-evidence-ban-v1`
- Aggregate tests:
  - `tests/runtime/test_evidence_integrity_gate_v1.py`
  - `tests/runtime/test_synthetic_evidence_ban_v1.py`

### Done criteria

- Release-bound artifacts include runtime provenance fields and trace links.
- Synthetic-only artifacts are rejected by gate policy.
- Evidence-integrity gates are release-blocking in local and CI lanes.

## M41: Process + Readiness Compatibility Closure v1

### Objective

Close high-impact process/readiness gaps needed for mainstream userspace
workloads while keeping deterministic behavior guarantees.

### PR-1 (contract freeze)

- Docs:
  - `docs/abi/compat_profile_v5.md`
  - `docs/runtime/syscall_coverage_matrix_v4.md`
  - `docs/abi/process_model_v4.md`
  - `docs/abi/readiness_io_model_v1.md`
- Tests:
  - `tests/compat/test_compat_docs_v5.py`

### PR-2 (implementation + campaigns)

- Tooling:
  - `tools/run_compat_surface_campaign_v2.py`
  - `tools/run_posix_gap_report_v2.py`
- Tests:
  - `tests/compat/test_fork_clone_surface_v1.py`
  - `tests/compat/test_epoll_surface_v1.py`
  - `tests/compat/test_process_model_v4.py`
  - `tests/compat/test_deferred_surface_behavior_v2.py`

### PR-3 (gate + closure)

- Gates:
  - `test-process-readiness-parity-v1`
  - sub-gate `test-posix-gap-closure-v2`
- Aggregate tests:
  - `tests/compat/test_process_readiness_gate_v1.py`
  - `tests/compat/test_posix_gap_closure_gate_v2.py`

### Done criteria

- Process/readiness compatibility commitments are runtime-verified.
- Deferred surfaces remain explicit and deterministically enforced.
- Process/readiness gates are release-blocking in local and CI lanes.

## M42: Isolation + Namespace Baseline v1

### Objective

Add a bounded, testable multi-tenant isolation baseline needed by modern
service/container workloads.

### PR-1 (contract freeze)

- Docs:
  - `docs/abi/namespace_cgroup_contract_v1.md`
  - `docs/security/isolation_profile_v1.md`
  - `docs/runtime/resource_control_policy_v1.md`
- Tests:
  - `tests/security/test_isolation_docs_v1.py`

### PR-2 (implementation + campaigns)

- Tooling:
  - `tools/run_isolation_campaign_v1.py`
  - `tools/run_resource_control_campaign_v1.py`
- Tests:
  - `tests/security/test_namespace_baseline_v1.py`
  - `tests/security/test_cgroup_baseline_v1.py`
  - `tests/security/test_isolation_escape_negative_v1.py`
  - `tests/runtime/test_resource_control_policy_v1.py`

### PR-3 (gate + closure)

- Gates:
  - `test-isolation-baseline-v1`
  - sub-gate `test-namespace-cgroup-v1`
- Aggregate tests:
  - `tests/security/test_isolation_gate_v1.py`
  - `tests/security/test_namespace_cgroup_gate_v1.py`

### Done criteria

- Isolation and resource controls are bounded, documented, and executable.
- Escape and privilege-escalation negative paths are deterministic.
- Isolation gates are release-blocking in local and CI lanes.

## M43: Hardware/Firmware Breadth + SMP v1

### Objective

Move from mostly virtualized release confidence to broader native-driver and
firmware/CPU-topology confidence.

### PR-1 (contract freeze)

- Docs:
  - `docs/hw/support_matrix_v5.md`
  - `docs/hw/driver_lifecycle_contract_v5.md`
  - `docs/hw/acpi_uefi_hardening_v3.md`
  - `docs/runtime/smp_interrupt_model_v1.md`
- Tests:
  - `tests/hw/test_hw_matrix_docs_v5.py`

### PR-2 (implementation + diagnostics)

- Tooling:
  - `tools/run_hw_matrix_v5.py`
  - `tools/collect_firmware_smp_evidence_v1.py`
- Tests:
  - `tests/hw/test_native_storage_driver_matrix_v1.py`
  - `tests/hw/test_native_nic_driver_matrix_v1.py`
  - `tests/hw/test_firmware_table_validation_v3.py`
  - `tests/hw/test_smp_interrupt_baseline_v1.py`

### PR-3 (gate + closure)

- Gates:
  - `test-hw-firmware-smp-v1`
  - sub-gate `test-native-driver-matrix-v1`
- Aggregate tests:
  - `tests/hw/test_hw_firmware_smp_gate_v1.py`
  - `tests/hw/test_native_driver_matrix_gate_v1.py`

### Done criteria

- Native driver and firmware/SMP claims are bounded by repeatable evidence.
- Unsupported targets remain explicit and non-claiming.
- Hardware/firmware/SMP gates are release-blocking in local and CI lanes.

## M44: Real Desktop + Ecosystem Qualification v2

### Objective

Promote desktop/app/package claims from model-heavy simulation to runtime-backed
qualification against signed, reproducible workload sets.

### PR-1 (contract freeze)

- Docs:
  - `docs/desktop/desktop_profile_v2.md`
  - `docs/abi/app_compat_tiers_v2.md`
  - `docs/pkg/ecosystem_scale_policy_v2.md`
  - `docs/pkg/distribution_workflow_v2.md`
- Tests:
  - `tests/desktop/test_desktop_docs_v2.py`
  - `tests/pkg/test_ecosystem_scale_docs_v2.py`

### PR-2 (implementation + qualification campaigns)

- Tooling:
  - `tools/run_real_gui_app_matrix_v2.py`
  - `tools/run_real_pkg_install_campaign_v2.py`
  - `tools/run_real_catalog_audit_v2.py`
- Tests:
  - `tests/desktop/test_gui_runtime_qualification_v2.py`
  - `tests/pkg/test_pkg_install_success_rate_v2.py`
  - `tests/pkg/test_catalog_reproducibility_v2.py`
  - `tests/pkg/test_distribution_workflow_v2.py`

### PR-3 (gate + closure)

- Gates:
  - `test-real-ecosystem-desktop-v2`
  - sub-gate `test-real-app-catalog-v2`
- Aggregate tests:
  - `tests/desktop/test_real_desktop_gate_v2.py`
  - `tests/pkg/test_real_catalog_gate_v2.py`

### Done criteria

- Desktop and package/app claims are backed by runtime-qualified artifacts.
- Signed provenance and reproducibility remain release-blocking.
- Real ecosystem/desktop gates are required in local and CI release lanes.

## Consolidated Makefile target stubs

```make
test-evidence-integrity-v1:
	$(PYTHON) -m pytest tests/runtime/test_evidence_integrity_gate_v1.py -v

test-synthetic-evidence-ban-v1:
	$(PYTHON) -m pytest tests/runtime/test_synthetic_evidence_ban_v1.py -v

test-process-readiness-parity-v1:
	$(PYTHON) -m pytest tests/compat/test_process_readiness_gate_v1.py -v

test-posix-gap-closure-v2:
	$(PYTHON) -m pytest tests/compat/test_posix_gap_closure_gate_v2.py -v

test-isolation-baseline-v1:
	$(PYTHON) -m pytest tests/security/test_isolation_gate_v1.py -v

test-namespace-cgroup-v1:
	$(PYTHON) -m pytest tests/security/test_namespace_cgroup_gate_v1.py -v

test-hw-firmware-smp-v1:
	$(PYTHON) -m pytest tests/hw/test_hw_firmware_smp_gate_v1.py -v

test-native-driver-matrix-v1:
	$(PYTHON) -m pytest tests/hw/test_native_driver_matrix_gate_v1.py -v

test-real-ecosystem-desktop-v2:
	$(PYTHON) -m pytest tests/desktop/test_real_desktop_gate_v2.py tests/pkg/test_real_catalog_gate_v2.py -v

test-real-app-catalog-v2:
	$(PYTHON) -m pytest tests/pkg/test_real_catalog_gate_v2.py -v
```

## Exit criteria for M40-M44 phase

This phase is complete only when all are true:

1. All M40-M44 primary gates are green in local and CI lanes.
2. All five cross-cutting sub-gates are green and artifact-backed.
3. Runtime evidence provenance is enforced for release-bound artifacts.
4. Compatibility/isolation/hardware claims are bounded to published pass
   history.
5. Desktop/ecosystem qualification is runtime-backed for declared workload
   classes.

## Risks and non-goals

- Non-goal: claim universal Linux/Windows parity in this phase.
- Non-goal: silently expand unsupported APIs without contract updates.
- Risk: widening scope without replacing synthetic evidence with runtime traces.
- Risk: claiming hardware/app support outside declared profile and pass history.
