# Support Lifecycle Policy v1

Date: 2026-03-09  
Milestone: M31 Release Engineering + Support Lifecycle v2  
Status: active release gate

## Objective

Define auditable support-window rules and backport/security response obligations
for active release branches.

## Policy identifier

- Support lifecycle policy ID: `rugo.support_lifecycle_policy.v1`
- Audit schema: `rugo.support_window_audit.v1`

## Required channels

- `stable`
- `lts`

## Window and SLA rules

- `stable`
  - minimum support window: 180 days
  - maximum security fix SLA: 14 days
  - minimum backport window: 21 days
- `lts`
  - minimum support window: 730 days
  - maximum security fix SLA: 14 days
  - minimum backport window: 180 days

## Audit fields

Each support-window audit entry must include:

- `channel`
- `support_days`
- `age_days`
- `in_support`
- `security_sla_days`
- `security_sla_within_threshold`
- `backport_window_days`
- `backport_window_meets_floor`

## Enforcement

- Support-window breaches are release-blocking.
- Security SLA breaches are release-blocking.
- Backport window floor breaches are release-blocking.
- Waivers require an explicit policy exception record and release-owner approval.

## Required gate hook

- Lifecycle gate: `make test-release-lifecycle-v2`
