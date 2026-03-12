# Namespace/Cgroup Contract v1

Date: 2026-03-10  
Milestone: M42 Isolation + Namespace Baseline v1  
Status: active release gate

## Objective

Define deterministic namespace/cgroup containment boundaries required for
multi-tenant service workloads in M42.

## Contract identity

- Namespace/cgroup contract ID: `rugo.namespace_cgroup_contract.v1`.
- Isolation profile ID: `rugo.isolation_profile.v1`.
- Resource control policy ID: `rugo.resource_control_policy.v1`.
- Isolation campaign schema: `rugo.isolation_campaign_report.v1`.
- Resource control report schema: `rugo.resource_control_report.v1`.

## Containment baseline

- Namespace isolation commitments:
  - PID namespace isolation for tenant process trees.
  - Mount namespace isolation for writable path boundaries.
  - UTS namespace isolation for host identity separation.
  - Network namespace isolation for tenant route/device boundaries.
- Cgroup baseline commitments:
  - CPU quota and throttling enforcement.
  - Memory hard-limit and OOM containment.
  - I/O weight and bandwidth governance.
  - PID controller limits for tenant process caps.

## Deterministic negative-path policy

- Cross-tenant and escape attempts must fail deterministically.
- Unsupported containment bypass operations must not silently succeed.
- Escape and privilege-escalation checks are release-blocking on policy drift.

## Default-Lane Runtime Evidence

The default `image-go` lane now carries a bounded runtime-backed isolation
proof in addition to the historical namespace/cgroup campaign artifacts:

- service domains are applied at launch time
- storage and network capabilities are task-bounded
- fd, socket, and endpoint limits are enforced on the live kernel path
- task snapshots expose `dom=`, `cap=`, `fd=`, and `sock=` markers
- shell exit cleanup is verified with `ISOC5: cleanup ok`
- runtime gate: `make test-reliable-isolated-runtime-c5`

## Gate requirements

- Isolation campaign command:
  - `python tools/run_isolation_campaign_v1.py --out out/isolation-campaign-v1.json`
- Resource-control campaign command:
  - `python tools/run_resource_control_campaign_v1.py --out out/resource-control-v1.json`
- Local gate: `make test-isolation-baseline-v1`.
- Local sub-gate: `make test-namespace-cgroup-v1`.
- Runtime closure gate: `make test-reliable-isolated-runtime-c5`.
- CI gate: `Isolation baseline v1 gate`.
- CI sub-gate: `Namespace cgroup v1 gate`.

Gate pass requires:

- isolation campaign `gate_pass = true`
- resource-control campaign `gate_pass = true`
- deterministic escape-denial checks remain satisfied

## Related contracts

- `docs/security/isolation_profile_v1.md`
- `docs/runtime/resource_control_policy_v1.md`
- `docs/abi/compat_profile_v5.md`
