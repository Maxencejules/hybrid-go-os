# IPv6 Baseline v1

Date: 2026-03-04  
Milestone: M12 Network Stack v1

## Purpose

Define the minimal IPv6 behavior required for M12 closure.

## Addressing baseline

- Link-local addressing support (`fe80::/64`).
- Static unicast addressing path for deterministic test environments.
- Deterministic source-address selection for baseline tests.

## Neighbor discovery baseline

- Neighbor Solicitation (NS) send/receive behavior.
- Neighbor Advertisement (NA) processing and cache update behavior.
- Deterministic stale/refresh policy for neighbor cache entries.

## ICMPv6 essentials

- Echo request/reply handling for baseline diagnostics.
- Required ICMPv6 control path handling for ND.
- Deterministic handling for unsupported ICMPv6 types.

## Non-goals in v1

- Full SLAAC lifecycle.
- Full DHCPv6 client behavior.
- Full extension-header and fragmentation parity.

## Evidence

- `tests/net/test_ipv6_nd_icmpv6_v1.py`
- `tools/run_net_interop_matrix_v1.py`
