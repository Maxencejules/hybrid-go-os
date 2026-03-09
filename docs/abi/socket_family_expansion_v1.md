# Socket Family Expansion v1

Date: 2026-03-09  
Milestone: M36 Compatibility Surface Expansion v1  
Status: active release gate

## Objective

Define bounded socket-family expansion commitments beyond the earlier subset
surface while preserving deterministic unsupported behavior for deferred
families.

## Contract identifiers

- Socket family contract ID: `rugo.socket_family_expansion.v1`
- Parent compatibility profile ID: `rugo.compat_profile.v4`
- Surface campaign schema: `rugo.compat_surface_campaign_report.v1`

## Required socket checks

- `socket_af_inet_stream`
  - `AF_INET` stream connect path is deterministic.
  - threshold: connect latency `<= 18 ms`.
- `socket_af_inet6_dgram`
  - `AF_INET6` datagram send/recv path is deterministic.
  - threshold: roundtrip latency `<= 20 ms`.
- `socket_af_unix_stream`
  - bounded `AF_UNIX` stream subset is deterministic.
  - threshold: connect latency `<= 12 ms`.
- `socket_af_unix_dgram`
  - bounded `AF_UNIX` datagram subset is deterministic.
  - threshold: roundtrip latency `<= 14 ms`.

Required messaging APIs in v1:

- `sendmsg`
- `recvmsg`
- `socketpair`

## Deferred families and semantics

The following remain deferred in M36:

- `AF_NETLINK`
- raw packet socket parity
- `epoll`/`io_uring` readiness family parity

Deferred socket families and readiness APIs must fail deterministically with
`-1`, `ENOSYS`.

## Tooling and gate wiring

- Campaign runner: `tools/run_compat_surface_campaign_v1.py`
- POSIX gap runner: `tools/run_posix_gap_report_v1.py`
- Local gate: `make test-compat-surface-v1`
- Local sub-gate: `make test-posix-gap-closure-v1`
- CI gate: `Compatibility surface v1 gate`
- CI sub-gate: `POSIX gap closure v1 gate`
