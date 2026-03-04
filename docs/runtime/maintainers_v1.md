# Runtime Port Maintainers v1

Date: 2026-03-04  
Milestone: M11 Runtime + Toolchain Maturity v1

## Ownership map

| Area | Maintainer ID | Responsibility |
|---|---|---|
| runtime port contract | `runtime-port-owner` | Owns `docs/runtime/port_contract_v1.md` and runtime ABI updates |
| runtime test gate | `runtime-test-owner` | Owns `tests/runtime/*` and `make test-runtime-maturity` signal quality |
| toolchain lane | `runtime-toolchain-owner` | Owns `tools/build_go_std_spike.sh`, `tools/runtime_toolchain_contract_v1.py`, bootstrap flow |
| CI gate | `runtime-ci-owner` | Owns CI runtime gate and artifact retention policy |
| milestone docs | `runtime-doc-owner` | Owns M11 evidence updates in `MILESTONES.md`, `docs/STATUS.md`, `README.md` |

## Breakage policy

- Runtime gate failures are release-blocking.
- ABI-impacting runtime changes require:
  - update to `docs/runtime/abi_stability_policy_v1.md`,
  - update to `docs/runtime/syscall_coverage_matrix_v1.md`,
  - linked test updates in `tests/runtime/`.
- Any deferred runtime coverage row must include an owner and target milestone.

## Escalation

- CI runtime gate red for >24h: notify `runtime-ci-owner` and
  `runtime-port-owner`.
- Reproducibility mismatch: notify `runtime-toolchain-owner` and block release
  tagging until resolved.
