# M35-M39 General-Purpose Expansion Roadmap (Post-M34)

Date: 2026-03-09  
Lane: Rugo (Rust kernel + Go user space)  
Status: Proposed

## Why this document exists

M21-M34 delivered a maturity-qualified baseline with deterministic gates and LTS
policy. This roadmap defines the next backlog set for the immediate gap areas
that remain before broad "general-purpose OS" parity expectations:

1. Desktop/GUI stack scope.
2. Deeper Linux/POSIX compatibility closure.
3. Hardware breadth beyond the current matrix focus.
4. Storage/platform feature breadth beyond current reliability scope.
5. Ecosystem/app scale beyond current tiered compatibility counts.

This is a contract-first execution plan, not an immediate parity claim.

## Scope and boundaries

In scope:
- Start and execute M35-M39 immediately.
- Keep deterministic, machine-verifiable contracts and release gates.
- Expand capability claims only when supported by gate evidence.

Out of scope:
- Declaring multi-year maturity proof complete in this phase.
- Claiming universal parity with Linux/Windows/macOS internals.

## Sequencing map

| Milestone | Focus | Primary gate |
|---|---|---|
| M35 | Desktop + Interactive UX Baseline v1 | `test-desktop-stack-v1` |
| M36 | Compatibility Surface Expansion v1 | `test-compat-surface-v1` |
| M37 | Hardware Breadth + Driver Matrix v4 | `test-hw-matrix-v4` |
| M38 | Storage + Platform Feature Expansion v1 | `test-storage-platform-v1` |
| M39 | Ecosystem Scale + Distribution Workflow v1 | `test-ecosystem-scale-v1` |

### Cross-cutting sub-gates (required)

| Sub-gate | Anchored milestone | Focus |
|---|---|---|
| `test-gui-app-compat-v1` | M35 | GUI app launch/runtime/input baseline |
| `test-posix-gap-closure-v1` | M36 | deferred syscall/API closures and deterministic unsupported behavior |
| `test-hw-baremetal-promotion-v1` | M37 | repeated bare-metal evidence and promotion policy |
| `test-storage-feature-contract-v1` | M38 | snapshots/resize/advanced FS semantics contract compliance |
| `test-app-catalog-health-v1` | M39 | package catalog quality, install success, reproducibility budgets |

## Suggested cadence

- Planning cadence: 1 milestone per 8-12 weeks.
- Each milestone follows the established 3-PR pattern:
  - PR-1: contract freeze,
  - PR-2: implementation and tooling,
  - PR-3: release-gate wiring and closure.

## M35: Desktop + Interactive UX Baseline v1

### Objective

Promote desktop/GUI from explicit out-of-scope to a bounded, testable baseline
covering graphics session bring-up, input, and basic desktop application class
execution.

### PR-1 (contract freeze)

- Docs:
  - `docs/desktop/display_stack_contract_v1.md`
  - `docs/desktop/window_manager_contract_v1.md`
  - `docs/desktop/input_stack_contract_v1.md`
  - `docs/desktop/desktop_profile_v1.md`
- Tests:
  - `tests/desktop/test_desktop_docs_v1.py`

### PR-2 (implementation + deterministic artifacts)

- Tooling:
  - `tools/run_desktop_smoke_v1.py`
  - `tools/run_gui_app_matrix_v1.py`
- Tests:
  - `tests/desktop/test_display_session_v1.py`
  - `tests/desktop/test_input_baseline_v1.py`
  - `tests/desktop/test_window_lifecycle_v1.py`
  - `tests/desktop/test_gui_app_compat_v1.py`

### PR-3 (gate + closure)

- Gates:
  - `test-desktop-stack-v1`
  - Sub-gate `test-gui-app-compat-v1`
- Aggregate tests:
  - `tests/desktop/test_desktop_gate_v1.py`
  - `tests/desktop/test_gui_app_compat_gate_v1.py`

### Done criteria

- Desktop baseline contracts are explicit and versioned.
- GUI baseline is deterministic in declared profiles.
- Desktop and GUI sub-gates are release-blocking in local and CI lanes.

## M36: Compatibility Surface Expansion v1

### Objective

Close high-impact compatibility gaps beyond v2/v3 subset boundaries while
preserving deterministic failure semantics for still-unsupported surfaces.

### PR-1 (contract freeze)

- Docs:
  - `docs/abi/compat_profile_v4.md`
  - `docs/runtime/syscall_coverage_matrix_v3.md`
  - `docs/abi/process_model_v3.md`
  - `docs/abi/socket_family_expansion_v1.md`
- Tests:
  - `tests/compat/test_compat_docs_v4.py`

### PR-2 (implementation + compatibility campaigns)

- Tooling:
  - `tools/run_compat_surface_campaign_v1.py`
  - `tools/run_posix_gap_report_v1.py`
- Tests:
  - `tests/compat/test_posix_gap_closure_v1.py`
  - `tests/compat/test_process_model_v3.py`
  - `tests/compat/test_socket_family_expansion_v1.py`
  - `tests/compat/test_deferred_surface_behavior_v1.py`

### PR-3 (gate + closure)

- Gates:
  - `test-compat-surface-v1`
  - Sub-gate `test-posix-gap-closure-v1`
- Aggregate tests:
  - `tests/compat/test_compat_surface_gate_v1.py`
  - `tests/compat/test_posix_gap_closure_gate_v1.py`

### Done criteria

- Expanded compatibility surface is contractized and test-backed.
- Deferred surfaces remain explicitly documented and deterministically enforced.
- Compatibility surface and sub-gate are release-blocking in local/CI lanes.

## M37: Hardware Breadth + Driver Matrix v4

### Objective

Expand hardware confidence from current matrix scope to broader bare-metal and
device-class coverage with deterministic promotion policy.

### PR-1 (contract freeze)

- Docs:
  - `docs/hw/support_matrix_v4.md`
  - `docs/hw/driver_lifecycle_contract_v4.md`
  - `docs/hw/bare_metal_promotion_policy_v1.md`
- Tests:
  - `tests/hw/test_hw_matrix_docs_v4.py`

### PR-2 (implementation + diagnostics)

- Tooling:
  - `tools/run_hw_matrix_v4.py`
  - `tools/collect_hw_promotion_evidence_v1.py`
- Tests:
  - `tests/hw/test_hw_matrix_v4.py`
  - `tests/hw/test_driver_lifecycle_v4.py`
  - `tests/hw/test_baremetal_promotion_v1.py`
  - `tests/hw/test_hw_negative_paths_v4.py`

### PR-3 (gate + closure)

- Gates:
  - `test-hw-matrix-v4`
  - Sub-gate `test-hw-baremetal-promotion-v1`
- Aggregate tests:
  - `tests/hw/test_hw_gate_v4.py`
  - `tests/hw/test_hw_baremetal_promotion_gate_v1.py`

### Done criteria

- v4 matrix tier claims are bounded to repeatable evidence.
- Bare-metal promotion thresholds are explicit and enforced.
- Hardware gates are release-blocking in local/CI lanes.

## M38: Storage + Platform Feature Expansion v1

### Objective

Move from reliability-only storage posture to broader platform feature coverage
including advanced filesystem operations and deterministic lifecycle behavior.

### PR-1 (contract freeze)

- Docs:
  - `docs/storage/fs_feature_contract_v1.md`
  - `docs/storage/snapshot_policy_v1.md`
  - `docs/storage/online_resize_policy_v1.md`
  - `docs/runtime/platform_feature_profile_v1.md`
- Tests:
  - `tests/storage/test_storage_feature_docs_v1.py`

### PR-2 (implementation + feature campaigns)

- Tooling:
  - `tools/run_storage_feature_campaign_v1.py`
  - `tools/run_platform_feature_conformance_v1.py`
- Tests:
  - `tests/storage/test_snapshot_semantics_v1.py`
  - `tests/storage/test_online_resize_v1.py`
  - `tests/storage/test_advanced_fs_ops_v1.py`
  - `tests/runtime/test_platform_feature_profile_v1.py`

### PR-3 (gate + closure)

- Gates:
  - `test-storage-platform-v1`
  - Sub-gate `test-storage-feature-contract-v1`
- Aggregate tests:
  - `tests/storage/test_storage_platform_gate_v1.py`
  - `tests/storage/test_storage_feature_contract_gate_v1.py`

### Done criteria

- Advanced storage/platform features are versioned and deterministic.
- Feature semantics are regression-gated with machine-readable artifacts.
- Storage/platform gates are release-blocking in local/CI lanes.

## M39: Ecosystem Scale + Distribution Workflow v1

### Objective

Scale app/package ecosystem from limited tier counts to a broader, reproducible
catalog and distribution-grade workflow baseline.

### PR-1 (contract freeze)

- Docs:
  - `docs/pkg/ecosystem_scale_policy_v1.md`
  - `docs/pkg/catalog_quality_contract_v1.md`
  - `docs/pkg/distribution_workflow_v1.md`
- Tests:
  - `tests/pkg/test_ecosystem_scale_docs_v1.py`

### PR-2 (implementation + scale simulations)

- Tooling:
  - `tools/run_app_catalog_sim_v1.py`
  - `tools/run_pkg_install_success_campaign_v1.py`
  - `tools/run_reproducible_catalog_audit_v1.py`
- Tests:
  - `tests/pkg/test_app_catalog_sim_v1.py`
  - `tests/pkg/test_pkg_install_success_rate_v1.py`
  - `tests/pkg/test_catalog_reproducibility_v1.py`
  - `tests/pkg/test_distribution_workflow_v1.py`

### PR-3 (gate + closure)

- Gates:
  - `test-ecosystem-scale-v1`
  - Sub-gate `test-app-catalog-health-v1`
- Aggregate tests:
  - `tests/pkg/test_ecosystem_scale_gate_v1.py`
  - `tests/pkg/test_app_catalog_health_gate_v1.py`

### Done criteria

- Catalog quality and ecosystem scale thresholds are explicit and auditable.
- Install/rebuild success and reproducibility budgets are release-blocking.
- Ecosystem gates are required in local and CI release lanes.

## Consolidated Makefile target stubs

```make
# M35-M39 high-level gates

test-desktop-stack-v1:
	$(PYTHON) -m pytest tests/desktop/test_desktop_gate_v1.py -v

test-gui-app-compat-v1:
	$(PYTHON) -m pytest tests/desktop/test_gui_app_compat_gate_v1.py -v

test-compat-surface-v1:
	$(PYTHON) -m pytest tests/compat/test_compat_surface_gate_v1.py -v

test-posix-gap-closure-v1:
	$(PYTHON) -m pytest tests/compat/test_posix_gap_closure_gate_v1.py -v

test-hw-matrix-v4:
	$(PYTHON) -m pytest tests/hw/test_hw_gate_v4.py -v

test-hw-baremetal-promotion-v1:
	$(PYTHON) -m pytest tests/hw/test_hw_baremetal_promotion_gate_v1.py -v

test-storage-platform-v1:
	$(PYTHON) -m pytest tests/storage/test_storage_platform_gate_v1.py -v

test-storage-feature-contract-v1:
	$(PYTHON) -m pytest tests/storage/test_storage_feature_contract_gate_v1.py -v

test-ecosystem-scale-v1:
	$(PYTHON) -m pytest tests/pkg/test_ecosystem_scale_gate_v1.py -v

test-app-catalog-health-v1:
	$(PYTHON) -m pytest tests/pkg/test_app_catalog_health_gate_v1.py -v
```

## Exit criteria for M35-M39 phase

This phase is complete only when all are true:

1. All M35-M39 gates are green in local and CI lanes.
2. All five cross-cutting sub-gates are green and artifact-backed.
3. Desktop/GUI claims are bounded to declared profiles with reproducible tests.
4. Compatibility expansion claims are backed by explicit coverage matrices.
5. Hardware/storage/ecosystem claims are bounded to published pass history.

## Risks and non-goals

- Non-goal: claim universal app compatibility outside declared contracts.
- Non-goal: remove deterministic unsupported behavior for out-of-scope surfaces.
- Risk: widening scope without ownership; every new surface must have owner and
  gate before release claims.
- Risk: gate sprawl without artifact quality; schemas must stay stable and
  machine-readable.
