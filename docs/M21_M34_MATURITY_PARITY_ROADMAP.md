# M21-M34 Maturity Parity Roadmap (Post-M20)

Date: 2026-03-04  
Lane: Rugo (Rust kernel + Go user space)  
Status: Proposed
Revision: 2026-03-05 (best-practice parity addenda)

## Why this document exists

M15-M20 defines the path to a serious multi-purpose baseline. This roadmap extends
beyond that point and defines the milestones required to approach the stability
and maturity profile of long-lived production OS families.

This is a milestone and gate plan, not a claim of current parity.

## Maturity target definition

For this roadmap, "parity-like maturity" means all of the following are true:

1. Stable ABI/API windows are enforced across multiple releases.
2. Hardware support claims are evidence-bounded and reproducible.
3. External app compatibility is broad enough for common workloads.
4. Security response, hardening, and release processes are operationally proven.
5. Update, rollback, recovery, observability, and support workflows are routine.
6. Governance and long-term maintenance are sustainable.

## Roadmap phases

| Phase | Milestones | Outcome |
|---|---|---|
| Phase A: Platform hardening | M21-M24 | Kernel and hardware/reliability confidence across releases |
| Phase B: Ecosystem expansion | M25-M28 | Practical software compatibility and stronger security posture |
| Phase C: Operability and lifecycle | M29-M32 | Distribution-grade operational workflows and policy maturity |
| Phase D: Qualification and LTS | M33-M34 | Long-window maturity qualification and public LTS baseline |

## Sequencing map

| Milestone | Focus | Primary gate |
|---|---|---|
| M21 | ABI + API Stability Program v3 | `test-abi-stability-v3` |
| M22 | Kernel Reliability + Soak v1 | `test-kernel-reliability-v1` |
| M23 | Hardware Enablement Matrix v3 | `test-hw-matrix-v3` |
| M24 | Performance Baseline + Regression Budgets v1 | `test-perf-regression-v1` |
| M25 | Userspace Service Model + Init v2 | `test-userspace-model-v2` |
| M26 | Package/Repo Ecosystem v3 | `test-pkg-ecosystem-v3` |
| M27 | External App Compatibility Program v3 | `test-app-compat-v3` |
| M28 | Security Hardening Program v3 | `test-security-hardening-v3` |
| M29 | Observability + Diagnostics v2 | `test-observability-v2` |
| M30 | Installer/Upgrade/Recovery UX v3 | `test-ops-ux-v3` |
| M31 | Release Engineering + Support Lifecycle v2 | `test-release-lifecycle-v2` |
| M32 | Conformance + Profile Qualification v1 | `test-conformance-v1` |
| M33 | Fleet-Scale Operations Baseline v1 | `test-fleet-ops-v1` |
| M34 | Maturity Qualification + LTS Declaration | `test-maturity-qual-v1` |

### Cross-cutting sub-gates (must be integrated into milestone gates)

| Sub-gate | Anchored milestone | Focus |
|---|---|---|
| `test-firmware-attestation-v1` | M23 | Measured boot, TPM event log, firmware resiliency |
| `test-update-trust-v1` | M26 | Metadata expiry/freeze/mix-and-match/rollback/key rotation |
| `test-vuln-response-v1` | M28 | PSIRT intake, advisory/CVE workflow, embargo drills |
| `test-crash-dump-v1` | M29 | Panic dump capture, symbolization, triage bundle |
| `test-supply-chain-revalidation-v1` | M31 | SBOM/provenance/signature revalidation + drift checks |
| `test-fleet-rollout-safety-v1` | M33 | Canary rollout policy, blast-radius budgets, SLO auto-halt |

## Suggested cadence

- Planning cadence: 1 milestone per 6-10 weeks.
- Each milestone follows the established 3-PR pattern:
  - PR-1: contract and policy freeze,
  - PR-2: implementation + tooling,
  - PR-3: local/CI gate and closure.

## M21: ABI + API Stability Program v3

### Objective

Make ABI/API stability predictable over multi-release windows with explicit
versioning, deprecation, and compatibility obligations.

### PR-1 (contract freeze)

- Docs:
  - `docs/abi/syscall_v3.md`
  - `docs/runtime/abi_stability_policy_v2.md`
  - `docs/runtime/deprecation_window_policy_v1.md`
- Tests:
  - `tests/runtime/test_abi_docs_v3.py`
  - `tests/runtime/test_abi_window_v3.py`

### PR-2 (compatibility enforcement)

- Tooling:
  - `tools/check_abi_diff_v3.py`
  - `tools/check_syscall_compat_v3.py`
- Tests:
  - `tests/runtime/test_abi_diff_gate_v3.py`
  - `tests/compat/test_abi_compat_matrix_v3.py`

### PR-3 (gate + closure)

- Gate:
  - Makefile target `test-abi-stability-v3`
  - CI step `ABI stability v3 gate`
- Aggregate test:
  - `tests/runtime/test_abi_stability_gate_v3.py`

### Done criteria

- ABI changes are tracked by machine-readable diff and policy checks.
- Breaking changes require explicit version bump + migration docs.

## M22: Kernel Reliability + Soak v1

### Objective

Prove long-run kernel stability under mixed workload stress and fault injection.

### PR-1

- Docs:
  - `docs/runtime/kernel_reliability_model_v1.md`
- Tests:
  - `tests/stress/test_kernel_soak_24h_v1.py`
  - `tests/stress/test_fault_injection_matrix_v1.py`

### PR-2

- Tooling:
  - `tools/run_kernel_soak_v1.py`
  - `tools/run_fault_campaign_kernel_v1.py`
- Tests:
  - `tests/stress/test_reliability_artifact_schema_v1.py`

### PR-3

- Gate:
  - `test-kernel-reliability-v1`
- Aggregate test:
  - `tests/stress/test_kernel_reliability_gate_v1.py`

### Done criteria

- Reliability thresholds are explicitly versioned.
- Soak/fault reports are release artifacts and gate-blocking.

## M23: Hardware Enablement Matrix v3

### Objective

Expand from matrix v2 to broader real-hardware confidence and driver lifecycle
consistency.

### PR-1

- Docs:
  - `docs/hw/support_matrix_v3.md`
  - `docs/hw/driver_lifecycle_contract_v3.md`
  - `docs/hw/firmware_resiliency_policy_v1.md`
  - `docs/security/measured_boot_attestation_v1.md`
- Tests:
  - `tests/hw/test_hardware_matrix_v3.py`
  - `tests/hw/test_driver_lifecycle_v3.py`
  - `tests/hw/test_firmware_resiliency_docs_v1.py`

### PR-2

- Tests:
  - `tests/hw/test_suspend_resume_v1.py`
  - `tests/hw/test_hotplug_baseline_v1.py`
  - `tests/hw/test_measured_boot_attestation_v1.py`
  - `tests/hw/test_tpm_eventlog_schema_v1.py`
- Tooling:
  - `tools/collect_hw_diagnostics_v3.py`
  - `tools/collect_measured_boot_report_v1.py`

### PR-3

- Gate:
  - `test-hw-matrix-v3`
  - Sub-gate `test-firmware-attestation-v1`
- Aggregate test:
  - `tests/hw/test_hw_gate_v3.py`
  - `tests/hw/test_firmware_attestation_gate_v1.py`

### Done criteria

- Tier claims reflect measured pass history.
- Driver init/runtime/error paths are testable and deterministic.
- Firmware resiliency controls are explicit and exercised by recovery drills.
- Measured boot attestation evidence is produced and policy-checked per release.

## M24: Performance Baseline + Regression Budgets v1

### Objective

Establish objective performance baselines and reject regressions automatically.

### PR-1

- Docs:
  - `docs/runtime/performance_budget_v1.md`
  - `docs/runtime/benchmark_policy_v1.md`
- Tests:
  - `tests/runtime/test_perf_budget_docs_v1.py`

### PR-2

- Tooling:
  - `tools/run_perf_baseline_v1.py`
  - `tools/check_perf_regression_v1.py`
- Tests:
  - `tests/runtime/test_perf_regression_v1.py`

### PR-3

- Gate:
  - `test-perf-regression-v1`
- Aggregate test:
  - `tests/runtime/test_perf_gate_v1.py`

### Done criteria

- Performance budgets exist for key workload classes.
- Regressions above threshold block release lanes.

## M25: Userspace Service Model + Init v2

### Objective

Stabilize service lifecycle semantics (init/service management/dependency handling)
for multi-purpose operation.

### PR-1

- Docs:
  - `docs/runtime/service_model_v2.md`
  - `docs/runtime/init_contract_v2.md`
- Tests:
  - `tests/runtime/test_service_model_docs_v2.py`

### PR-2

- Tests:
  - `tests/runtime/test_service_lifecycle_v2.py`
  - `tests/runtime/test_service_dependency_order_v2.py`
  - `tests/runtime/test_restart_policy_v2.py`

### PR-3

- Gate:
  - `test-userspace-model-v2`
- Aggregate test:
  - `tests/runtime/test_userspace_model_gate_v2.py`

### Done criteria

- Service startup/shutdown/restart/failure semantics are explicit and tested.
- Boot-to-operational state is deterministic.

## M26: Package/Repo Ecosystem v3

### Objective

Move from update pipeline maturity to practical package ecosystem operation with
policy, metadata quality, and lifecycle controls.

### PR-1

- Docs:
  - `docs/pkg/package_format_v3.md`
  - `docs/pkg/repository_policy_v3.md`
  - `docs/pkg/update_trust_model_v1.md`
  - `docs/security/update_key_rotation_policy_v1.md`
- Tests:
  - `tests/pkg/test_pkg_contract_docs_v3.py`
  - `tests/pkg/test_update_trust_docs_v1.py`

### PR-2

- Tooling:
  - `tools/repo_policy_check_v3.py`
  - `tools/pkg_rebuild_verify_v3.py`
  - `tools/check_update_trust_v1.py`
  - `tools/run_update_key_rotation_drill_v1.py`
- Tests:
  - `tests/pkg/test_pkg_rebuild_repro_v3.py`
  - `tests/pkg/test_repo_policy_v3.py`
  - `tests/pkg/test_update_metadata_expiry_v1.py`
  - `tests/pkg/test_update_freeze_attack_v1.py`
  - `tests/pkg/test_update_mix_and_match_v1.py`
  - `tests/pkg/test_update_key_rotation_v1.py`
### PR-3

- Gate:
  - `test-pkg-ecosystem-v3`
  - Sub-gate `test-update-trust-v1`
- Aggregate test:
  - `tests/pkg/test_pkg_ecosystem_gate_v3.py`
  - `tests/pkg/test_update_trust_gate_v1.py`

### Done criteria

- Package lifecycle policy is enforced by tools and tests.
- Rebuild and metadata integrity checks are release-blocking.
- Update trust model rejects expiry/freeze/mix-and-match/rollback attacks.
- Key rotation and trust-root transition drills are deterministic and auditable.

## M27: External App Compatibility Program v3

### Objective

Scale external application compatibility from curated demos to practical app
classes with repeatable pass thresholds.

### PR-1

- Docs:
  - `docs/abi/compat_profile_v3.md`
  - `docs/abi/app_compat_tiers_v1.md`
- Tests:
  - `tests/compat/test_app_tier_docs_v1.py`

### PR-2

- Tests:
  - `tests/compat/test_cli_suite_v3.py`
  - `tests/compat/test_runtime_suite_v3.py`
  - `tests/compat/test_service_suite_v3.py`
- Tooling:
  - `tools/run_app_compat_matrix_v3.py`

### PR-3

- Gate:
  - `test-app-compat-v3`
- Aggregate test:
  - `tests/compat/test_app_compat_gate_v3.py`

### Done criteria

- Compatibility tiers and pass thresholds are public and stable.
- External app compatibility reports are generated per release.

## M28: Security Hardening Program v3

### Objective

Evolve from baseline security controls to mature hardening and response posture.

### PR-1

- Docs:
  - `docs/security/hardening_profile_v3.md`
  - `docs/security/threat_model_v2.md`
  - `docs/security/vulnerability_response_policy_v1.md`
  - `docs/security/security_advisory_policy_v1.md`
- Tests:
  - `tests/security/test_hardening_docs_v3.py`
  - `tests/security/test_vuln_response_docs_v1.py`

### PR-2

- Tooling:
  - `tools/run_security_attack_suite_v3.py`
  - `tools/run_security_fuzz_v2.py`
  - `tools/security_advisory_lint_v1.py`
  - `tools/security_embargo_drill_v1.py`
- Tests:
  - `tests/security/test_attack_suite_v3.py`
  - `tests/security/test_fuzz_gate_v2.py`
  - `tests/security/test_policy_enforcement_v3.py`
  - `tests/security/test_vuln_triage_sla_v1.py`
  - `tests/security/test_embargo_workflow_v1.py`
  - `tests/security/test_advisory_schema_v1.py`

### PR-3

- Gate:
  - `test-security-hardening-v3`
  - Sub-gate `test-vuln-response-v1`
- Aggregate test:
  - `tests/security/test_security_hardening_gate_v3.py`
  - `tests/security/test_vuln_response_gate_v1.py`

### Done criteria

- Hardening profile is explicit and enforced in release lanes.
- Attack-suite and fuzzing outcomes are tracked with closure SLA.
- Vulnerability intake, triage, embargo handling, and advisory publication are policy-gated.
- CVE/advisory records are machine-validated and release-auditable.

## M29: Observability + Diagnostics v2

### Objective

Make operational diagnosis first-class with stable telemetry, tracing, and
support artifact contracts.

### PR-1

- Docs:
  - `docs/runtime/observability_contract_v2.md`
  - `docs/runtime/crash_dump_contract_v1.md`
  - `docs/runtime/postmortem_triage_playbook_v1.md`
- Tests:
  - `tests/runtime/test_observability_docs_v2.py`
  - `tests/runtime/test_crash_dump_docs_v1.py`

### PR-2

- Tooling:
  - `tools/collect_trace_bundle_v2.py`
  - `tools/collect_diagnostic_snapshot_v2.py`
  - `tools/collect_crash_dump_v1.py`
  - `tools/symbolize_crash_dump_v1.py`
- Tests:
  - `tests/runtime/test_trace_bundle_v2.py`
  - `tests/runtime/test_diag_snapshot_v2.py`
  - `tests/runtime/test_crash_dump_capture_v1.py`
  - `tests/runtime/test_crash_dump_symbolization_v1.py`

### PR-3

- Gate:
  - `test-observability-v2`
  - Sub-gate `test-crash-dump-v1`
- Aggregate test:
  - `tests/runtime/test_observability_gate_v2.py`
  - `tests/runtime/test_crash_dump_gate_v1.py`

### Done criteria

- Diagnostic artifacts are machine-readable and stable.
- Incident triage can be completed from standard support bundle outputs.
- Panic-to-dump-to-symbolized-triage flow is deterministic and release-tested.
- Crash dump retention and symbol mapping policies are documented and auditable.

## M30: Installer/Upgrade/Recovery UX v3

### Objective

Raise operational workflows from engineering-capable to robust day-to-day
administration quality.

### PR-1

- Docs:
  - `docs/build/installer_ux_v3.md`
  - `docs/build/recovery_workflow_v3.md`
- Tests:
  - `tests/build/test_installer_ux_v3.py`

### PR-2

- Tooling:
  - `tools/run_upgrade_drill_v3.py`
  - `tools/run_recovery_drill_v3.py`
- Tests:
  - `tests/build/test_upgrade_recovery_v3.py`
  - `tests/build/test_rollback_safety_v3.py`

### PR-3

- Gate:
  - `test-ops-ux-v3`
- Aggregate test:
  - `tests/build/test_ops_ux_gate_v3.py`

### Done criteria

- Install/upgrade/rollback/recovery drills are deterministic and release-blocking.
- Operator runbooks are complete and test-referenced.

## M31: Release Engineering + Support Lifecycle v2

### Objective

Formalize distribution-grade release lifecycle governance and support windows.

### PR-1

- Docs:
  - `docs/build/release_policy_v2.md`
  - `docs/build/support_lifecycle_policy_v1.md`
  - `docs/build/supply_chain_revalidation_policy_v1.md`
  - `docs/build/release_attestation_policy_v1.md`
- Tests:
  - `tests/build/test_release_policy_v2_docs.py`
  - `tests/build/test_supply_chain_revalidation_docs_v1.py`

### PR-2

- Tooling:
  - `tools/release_branch_audit_v2.py`
  - `tools/support_window_audit_v1.py`
  - `tools/verify_sbom_provenance_v2.py`
  - `tools/verify_release_attestations_v1.py`
- Tests:
  - `tests/build/test_release_branch_policy_v2.py`
  - `tests/build/test_support_window_policy_v1.py`
  - `tests/build/test_sbom_revalidation_v1.py`
  - `tests/build/test_provenance_verification_v1.py`
  - `tests/build/test_attestation_drift_v1.py`

### PR-3

- Gate:
  - `test-release-lifecycle-v2`
  - Sub-gate `test-supply-chain-revalidation-v1`
- Aggregate test:
  - `tests/build/test_release_lifecycle_gate_v2.py`
  - `tests/build/test_supply_chain_revalidation_gate_v1.py`

### Done criteria

- Release channels and support windows are policy-enforced and auditable.
- Backport and security fix obligations are explicit.
- SBOM/provenance/signature attestations are revalidated for every release candidate.
- Attestation drift is gate-blocking and requires explicit policy exception records.

## M32: Conformance + Profile Qualification v1

### Objective

Define profile-level conformance (server, developer workstation, appliance-like)
and qualify releases against profile requirements.

### PR-1

- Docs:
  - `docs/runtime/profile_conformance_v1.md`
- Tests:
  - `tests/runtime/test_profile_conformance_docs_v1.py`

### PR-2

- Tooling:
  - `tools/run_conformance_suite_v1.py`
- Tests:
  - `tests/runtime/test_server_profile_v1.py`
  - `tests/runtime/test_dev_profile_v1.py`

### PR-3

- Gate:
  - `test-conformance-v1`
- Aggregate test:
  - `tests/runtime/test_conformance_gate_v1.py`

### Done criteria

- Profile requirements are explicit and machine-verifiable.
- Release artifacts include profile qualification reports.

## M33: Fleet-Scale Operations Baseline v1

### Objective

Introduce controlled fleet-style operations (update orchestration, rollback
coordination, health policy) for multi-node environments.

### PR-1

- Docs:
  - `docs/pkg/fleet_update_policy_v1.md`
  - `docs/runtime/fleet_health_policy_v1.md`
  - `docs/pkg/staged_rollout_policy_v1.md`
  - `docs/runtime/canary_slo_policy_v1.md`
- Tests:
  - `tests/pkg/test_fleet_policy_docs_v1.py`
  - `tests/pkg/test_rollout_policy_docs_v1.py`

### PR-2

- Tooling:
  - `tools/run_fleet_update_sim_v1.py`
  - `tools/run_fleet_health_sim_v1.py`
  - `tools/run_canary_rollout_sim_v1.py`
  - `tools/run_rollout_abort_drill_v1.py`
- Tests:
  - `tests/pkg/test_fleet_update_sim_v1.py`
  - `tests/runtime/test_fleet_health_sim_v1.py`
  - `tests/pkg/test_canary_rollout_sim_v1.py`
  - `tests/runtime/test_rollout_abort_policy_v1.py`

### PR-3

- Gate:
  - `test-fleet-ops-v1`
  - Sub-gate `test-fleet-rollout-safety-v1`
- Aggregate test:
  - `tests/runtime/test_fleet_ops_gate_v1.py`
  - `tests/runtime/test_fleet_rollout_safety_gate_v1.py`

### Done criteria

- Multi-node policy behavior is deterministic and testable.
- Fleet update and rollback simulations are release artifacts.
- Canary rollout policies enforce blast-radius and automatic halt conditions.
- SLO-triggered abort and rollback coordination are deterministic and auditable.

## M34: Maturity Qualification + LTS Declaration

### Objective

Execute a final qualification cycle that proves long-window stability and
operational maturity, then declare an LTS baseline.

### PR-1

- Docs:
  - `docs/build/maturity_qualification_v1.md`
  - `docs/build/lts_declaration_policy_v1.md`
- Tests:
  - `tests/build/test_maturity_docs_v1.py`

### PR-2

- Tooling:
  - `tools/run_maturity_qualification_v1.py`
- Tests:
  - `tests/build/test_maturity_qualification_v1.py`
  - `tests/build/test_lts_policy_v1.py`
  - `tests/build/test_maturity_security_response_drill_v1.py`
  - `tests/build/test_maturity_supply_chain_continuity_v1.py`
  - `tests/build/test_maturity_rollout_safety_v1.py`

### PR-3

- Gate:
  - `test-maturity-qual-v1`
- Aggregate test:
  - `tests/build/test_maturity_gate_v1.py`
- Closure updates:
  - `MILESTONES.md`
  - `docs/STATUS.md`
  - `README.md`

### Done criteria

- Qualification bundle demonstrates multi-release stability evidence.
- LTS declaration criteria are met and publicly documented.
- Qualification bundle includes vulnerability-response drills and advisory/CVE audit trails.
- Qualification bundle includes measured-boot, crash-dump, and supply-chain revalidation evidence.
- Qualification bundle includes fleet canary/rollback safety metrics across multiple release cycles.

## Consolidated Makefile Target Stubs

```make
# M21-M34 high-level gates

test-abi-stability-v3:
	$(PYTHON) -m pytest tests/runtime/test_abi_stability_gate_v3.py -v

test-kernel-reliability-v1:
	$(PYTHON) -m pytest tests/stress/test_kernel_reliability_gate_v1.py -v

test-hw-matrix-v3:
	$(PYTHON) -m pytest tests/hw/test_hw_gate_v3.py -v

test-firmware-attestation-v1:
	$(PYTHON) -m pytest tests/hw/test_firmware_attestation_gate_v1.py -v

test-perf-regression-v1:
	$(PYTHON) -m pytest tests/runtime/test_perf_gate_v1.py -v

test-userspace-model-v2:
	$(PYTHON) -m pytest tests/runtime/test_userspace_model_gate_v2.py -v

test-pkg-ecosystem-v3:
	$(PYTHON) -m pytest tests/pkg/test_pkg_ecosystem_gate_v3.py -v

test-update-trust-v1:
	$(PYTHON) -m pytest tests/pkg/test_update_trust_gate_v1.py -v

test-app-compat-v3:
	$(PYTHON) -m pytest tests/compat/test_app_compat_gate_v3.py -v

test-security-hardening-v3:
	$(PYTHON) -m pytest tests/security/test_security_hardening_gate_v3.py -v

test-vuln-response-v1:
	$(PYTHON) -m pytest tests/security/test_vuln_response_gate_v1.py -v

test-observability-v2:
	$(PYTHON) -m pytest tests/runtime/test_observability_gate_v2.py -v

test-crash-dump-v1:
	$(PYTHON) -m pytest tests/runtime/test_crash_dump_gate_v1.py -v

test-ops-ux-v3:
	$(PYTHON) -m pytest tests/build/test_ops_ux_gate_v3.py -v

test-release-lifecycle-v2:
	$(PYTHON) -m pytest tests/build/test_release_lifecycle_gate_v2.py -v

test-supply-chain-revalidation-v1:
	$(PYTHON) -m pytest tests/build/test_supply_chain_revalidation_gate_v1.py -v

test-conformance-v1:
	$(PYTHON) -m pytest tests/runtime/test_conformance_gate_v1.py -v

test-fleet-ops-v1:
	$(PYTHON) -m pytest tests/runtime/test_fleet_ops_gate_v1.py -v

test-fleet-rollout-safety-v1:
	$(PYTHON) -m pytest tests/runtime/test_fleet_rollout_safety_gate_v1.py -v

test-maturity-qual-v1:
	$(PYTHON) -m pytest tests/build/test_maturity_gate_v1.py -v
```

## Final maturity exit criteria (M34)

The roadmap is considered complete only when all are true:

1. All M21-M34 gates are green in local and CI release lanes.
2. All cross-cutting sub-gates are green (`firmware-attestation`, `update-trust`, `vuln-response`, `crash-dump`, `supply-chain-revalidation`, `fleet-rollout-safety`).
3. ABI/API stability policy has held across multiple releases.
4. Hardware and compatibility claims are backed by published pass-history.
5. Security, reliability, observability, and recovery artifacts are produced per release.
6. Vulnerability response and advisory/CVE workflows are operationally proven with audit trails.
7. Support lifecycle policy, supply-chain revalidation policy, and LTS declaration are active and auditable.

## Non-goals of this roadmap

- Claiming immediate parity with every subsystem and ecosystem feature of
  Windows/macOS/Linux distributions.
- Replacing the need for multi-year operational proof with a single release.
- Expanding scope without corresponding contract, tests, and gate artifacts.
