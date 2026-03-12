# Socket Contract v2

Date: 2026-03-08  
Milestone: M19 Network Stack v2

## Scope

Define deterministic socket and DNS-stub behavior for the M19 lane. The
boot-backed C4 default-lane proof currently exercises the stream subset below.

## Supported socket surface

- Domains:
  - `AF_INET`
  - `AF_INET6`
- Types:
  - `SOCK_STREAM` on the live C4 lane
  - datagram or DNS-parity behavior remains part of the broader M19 contract
- Lifecycle calls:
  - `socket`, `bind`, `listen`, `connect`, `accept`, `close`
- Data calls:
  - `send`, `recv`
- Routing/config:
  - `sys_net_if_config`
  - `sys_net_route_add`
- Readiness:
  - generalized socket readiness remains additive future work

## Blocking and non-blocking semantics

- The live C4 lane exercises deterministic immediate connect/accept/send/recv
  on locally routed peers.
- Broader timeout, non-blocking, and shutdown behavior remains additive future
  work and must fail deterministically when unavailable.
- Unsupported options/extensions must fail deterministically as unsupported.

## DNS stub behavior

- Query classes in v2 baseline:
  - `A`
  - `AAAA`
- Required behavior:
  - deterministic answers for configured service names,
  - deterministic `NXDOMAIN` for unknown names,
  - TTL-bounded cache behavior with explicit expiry.
- Resolver fallback:
  - when no `AAAA` answer exists, dual-stack fallback must choose IPv4.
- DNS-stub behavior remains part of the broader M19 contract; it is not part of
  the current boot-backed C4 socket proof path.

## Error model

M19 follows deterministic error classes from `docs/abi/syscall_v1.md`:

- `E_INVAL`, `E_RANGE`, `E_FAULT`, `E_AGAIN`, `E_TIMEOUT`, `E_UNSUP`, `E_IO`

## Evidence

- Contract tests:
  - `tests/net/test_tcp_interop_v2.py`
  - `tests/net/test_ipv6_interop_v2.py`
  - `tests/net/test_dns_stub_v2.py`
  - `tests/runtime/test_connected_runtime_c4.py`
- Related baseline docs:
  - `docs/net/network_stack_contract_v2.md`
  - `docs/net/tcp_profile_v2.md`
  - `docs/net/interop_matrix_v2.md`
