# M10 Execution Backlog (Security Baseline v1)

Date: 2026-03-04  
Lane: Rugo (Rust kernel + Go user space)

## Goal

Drive M10 to an executable security baseline:

- enforce per-handle rights with reduction/transfer semantics,
- add per-process syscall/resource sandbox profile controls,
- validate signed boot artifacts with tamper rejection,
- run a continuous security fuzz gate with machine-readable reports,
- publish incident response and advisory workflow.

M10 source of truth remains `MILESTONES.md`, `docs/security/*`, and this
backlog.

## Current State Summary

- M9 hardware matrix v1 is complete and release-gated.
- M8 compatibility profile established deterministic syscall contracts.
- Package path already enforces payload hash checks (`PKG: hash ok`) but lacked
  a dedicated secure-boot artifact signature gate.

## Execution Result

- PR-1: complete (2026-03-04)
- PR-2: complete (2026-03-04)
- PR-3: complete (2026-03-04)

## PR-1: Rights Model + Kernel Enforcement

### Objective

Adopt explicit fd-handle rights and enforce them in kernel syscall paths.

### Scope

- Extend fd table entries with rights bitsets.
- Enforce rights in `sys_read/sys_write/sys_poll`.
- Extend the default Go lane with owner-only IPC receive/control rights and
  init-only service launch.
- Add rights-management syscalls:
  - `sys_fd_rights_get` (24)
  - `sys_fd_rights_reduce` (25)
  - `sys_fd_rights_transfer` (26)
- Add executable kernel acceptance path:
  - `sec_rights_test`
  - `tests/security/test_rights_enforcement.py`
  - `tests/security/test_go_service_policy_rights_v1.py`

### Primary files

- `kernel_rs/src/lib.rs`
- `services/security/sec_rights.asm`
- `services/go/runtime.go`
- `services/go/services.go`
- `tests/security/test_rights_enforcement.py`
- `tests/security/test_go_service_policy_rights_v1.py`
- `docs/security/rights_capability_model_v1.md`

## PR-2: Syscall Filtering + Secure Boot Manifest

### Objective

Add least-privilege syscall profile controls and trusted-boot artifact
verification workflow.

### Scope

- Add `sys_sec_profile_set` (27) and restricted profile allowlist.
- Enforce restricted-path policy for `sys_open`.
- Add executable filter acceptance path:
  - `sec_filter_test`
  - `tests/security/test_syscall_filter.py`
- Add boot-manifest signing/verification tool:
  - `tools/secure_boot_manifest_v1.py`
- Add tamper/key-rotation tests:
  - `tests/security/test_secure_boot_manifest_v1.py`

### Primary files

- `kernel_rs/src/lib.rs`
- `services/security/sec_filter.asm`
- `tools/secure_boot_manifest_v1.py`
- `docs/security/secure_boot_policy_v1.md`
- `docs/security/syscall_filtering_v1.md`

## PR-3: Fuzz Gate + Incident Process + Milestone Closure

### Objective

Add continuous security fuzz report gate, incident workflow docs, and close M10.

### Scope

- Add model-based security fuzz harness:
  - `tools/run_security_fuzz_v1.py`
  - `tests/security/test_security_fuzz_harness_v1.py`
- Add incident/advisory process docs:
  - `docs/security/incident_response_v1.md`
  - `docs/security/fuzzing_v1.md`
- Add local and CI security gate wiring.
- Mark M10 done in status/milestone docs.

### Primary files

- `Makefile` (`test-security-baseline`)
- `.github/workflows/ci.yml` (security baseline v1 gate)
- `MILESTONES.md`
- `docs/STATUS.md`
- `README.md`

## Acceptance checks

- `make test-security-baseline`
- `python -m pytest tests/security -v`
- `python tools/run_security_fuzz_v1.py --out out/security-fuzz-report.json`

## Non-goals for M10 backlog

- Full hardware-rooted secure boot chain implementation.
- Full sandbox policy language (seccomp-BPF parity).
- Kernel coverage instrumentation integration in this milestone.
