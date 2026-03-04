# Retransmission Timer Policy v1

Date: 2026-03-04  
Milestone: M12 Network Stack v1

## Purpose

Define deterministic retransmission and timeout behavior for M12 TCP baseline.

## Baseline policy

- Initial RTO baseline: 200 ms.
- Exponential backoff factor: 2x.
- Maximum retransmission attempts: 5.
- Maximum effective RTO cap: 3200 ms.

## Required deterministic behavior

- A lost/unacked segment schedules a retransmission timeout.
- Each timeout increments retry counter and applies bounded backoff.
- Valid ACK for all in-flight data clears pending retransmission state.
- After max retries, connection transitions to deterministic failure path.

## Failure-path policy

- Retry exhaustion maps to deterministic timeout behavior (`E_TIMEOUT`).
- Retransmission failure must not leave orphaned in-flight counters.
- Timer tick drift must not bypass retry caps.

## Evidence

- `tests/net/test_tcp_retransmission_v1.py`
- `tools/run_net_soak_v1.py`
