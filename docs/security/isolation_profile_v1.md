# Isolation Profile v1

Date: 2026-03-10  
Milestone: M42 Isolation + Namespace Baseline v1  
Status: active release gate

## Objective

Define deterministic tenant-isolation semantics and escape-denial requirements
for namespace/cgroup baseline enforcement.

## Contract identifiers

- Isolation profile ID: `rugo.isolation_profile.v1`
- Parent namespace/cgroup contract ID: `rugo.namespace_cgroup_contract.v1`
- Isolation campaign schema: `rugo.isolation_campaign_report.v1`
- Resource control report schema: `rugo.resource_control_report.v1`

## Required namespace checks

- `namespace_pid_isolation_ratio`: PID tree visibility remains tenant-bounded.
- `namespace_mount_isolation_ratio`: mount modifications remain tenant-bounded.
- `namespace_uts_isolation_ratio`: hostname/domainname remain tenant-bounded.
- `namespace_net_isolation_ratio`: network namespace boundaries remain tenant-bounded.

Thresholds:

- PID isolation ratio: `>= 1.0`
- mount isolation ratio: `>= 1.0`
- UTS isolation ratio: `>= 1.0`
- network isolation ratio: `>= 1.0`

## Required escape-negative checks

- `escape_setns_denied_ratio`: unprivileged `setns` escape attempts are denied.
- `escape_cross_tenant_signal_denied_ratio`: cross-tenant signal injections are denied.
- `escape_mount_propagation_block_ratio`: prohibited mount propagation escapes are denied.
- `escape_privilege_escalation_events`: successful escape/elevation events remain zero.
- `escape_namespace_leak_events`: namespace descriptor leak events remain zero.

Thresholds:

- setns denial ratio: `>= 1.0`
- cross-tenant signal denial ratio: `>= 1.0`
- mount propagation block ratio: `>= 1.0`
- privilege-escalation events: `<= 0`
- namespace leak events: `<= 0`

## Gate wiring

- Isolation campaign runner: `tools/run_isolation_campaign_v1.py`
- Local gate: `make test-isolation-baseline-v1`
- Local sub-gate: `make test-namespace-cgroup-v1`
- CI gate: `Isolation baseline v1 gate`
- CI sub-gate: `Namespace cgroup v1 gate`
