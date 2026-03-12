# Resource Control Policy v1

Date: 2026-03-10  
Milestone: M42 Isolation + Namespace Baseline v1  
Status: active release gate

## Objective

Define deterministic CPU, memory, I/O, and PID controller enforcement semantics
for M42 namespace/cgroup baseline claims.

## Policy identifiers

- Resource control policy ID: `rugo.resource_control_policy.v1`
- Parent namespace/cgroup contract ID: `rugo.namespace_cgroup_contract.v1`
- Isolation profile linkage: `rugo.isolation_profile.v1`
- Resource control report schema: `rugo.resource_control_report.v1`
- Requirement schema: `rugo.resource_control_requirement_set.v1`

## Required controller checks

CPU controller:

- `cpu_hard_quota_enforcement_ratio`
- `cpu_throttle_recovery_ms`
- `cpu_quota_violation_count`

Memory controller:

- `memory_hard_limit_enforcement_ratio`
- `memory_oom_reclaim_latency_ms`
- `memory_limit_breach_count`

I/O and PID controller:

- `io_bw_cap_enforcement_ratio`
- `io_latency_p99_ms`
- `pids_max_enforcement_ratio`

Global policy checks:

- `noisy_neighbor_containment_ratio`
- `controller_drift_events`
- `throttle_fairness_ratio`

## Thresholds

- CPU hard quota enforcement ratio: `>= 1.0`
- CPU throttle recovery latency: `<= 30 ms`
- CPU quota violation count: `<= 0`
- Memory hard limit enforcement ratio: `>= 1.0`
- Memory OOM reclaim latency: `<= 55 ms`
- Memory limit breach count: `<= 0`
- I/O bandwidth cap enforcement ratio: `>= 1.0`
- I/O p99 latency under cap: `<= 25 ms`
- PID max enforcement ratio: `>= 1.0`
- Noisy-neighbor containment ratio: `>= 1.0`
- Controller drift events: `<= 0`
- Throttle fairness ratio: `>= 0.98`

## Default-Lane Runtime Evidence

The shipped `image-go` lane now exercises a bounded runtime-backed resource
control profile alongside the original synthetic M42 campaigns:

- per-service fd, socket, and endpoint ceilings are configured at launch
- storage and network access are capability-gated
- quota-denial markers are emitted before cleanup verification
- task snapshots expose live `fd=` and `sock=` counts
- runtime gate: `make test-reliable-isolated-runtime-c5`

## Gate wiring

- Resource-control runner: `tools/run_resource_control_campaign_v1.py`
- Isolation campaign runner: `tools/run_isolation_campaign_v1.py`
- Local gate: `make test-isolation-baseline-v1`
- Local sub-gate: `make test-namespace-cgroup-v1`
- Runtime closure gate: `make test-reliable-isolated-runtime-c5`
- CI gate: `Isolation baseline v1 gate`
- CI sub-gate: `Namespace cgroup v1 gate`
