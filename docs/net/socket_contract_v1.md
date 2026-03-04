# Socket Contract v1

Date: 2026-03-04  
Milestone: M12 Network Stack v1

## Scope

Define deterministic socket semantics for the M12 baseline.

## Supported baseline surface

- Domains:
  - `AF_INET` required.
  - `AF_INET6` baseline required for IPv6 ND/ICMPv6 closure.
- Types:
  - `SOCK_DGRAM` (UDP baseline).
  - `SOCK_STREAM` (TCP baseline).
- Lifecycle calls:
  - `socket`, `bind`, `listen`, `connect`, `accept`, `close`, `shutdown`.
- Data calls:
  - `send`, `recv`, `sendto`, `recvfrom`.
- Readiness:
  - poll-style readiness semantics (`POLLIN`, `POLLOUT`, `POLLERR`).

## Blocking and non-blocking semantics

- Blocking mode:
  - operations may wait for readiness and must honor timeout bounds.
- Non-blocking mode:
  - operations must return immediately when not ready.
  - transient not-ready conditions map to deterministic retry behavior.
- Timeout semantics:
  - bounded wait returns timeout class behavior, not silent success.

## Poll readiness model

- `POLLIN`:
  - set when a stream has queued bytes or a listener has queued accepts.
  - set when datagram queue is non-empty.
- `POLLOUT`:
  - set when send path can accept payload for the socket type.
- `POLLERR`:
  - set for invalid descriptors or terminal error states.

## Error model

M12 follows ABI v1 deterministic error classes from `docs/abi/syscall_v1.md`:

- `E_INVAL`, `E_RANGE`, `E_FAULT`, `E_AGAIN`, `E_TIMEOUT`, `E_UNSUP`, `E_IO`

Unsupported socket options or unimplemented extensions must fail as
deterministic unsupported behavior (`E_UNSUP`), not as silent no-op.

## Non-goals in v1

- Full Linux socket option parity.
- Ancillary data/control message parity.
- Advanced TCP features (fast open, SACK tuning API, advanced CC variants).

## Evidence

- Contract tests:
  - `tests/net/test_socket_contract_docs_v1.py`
  - `tests/net/test_socket_poll_semantics_v1.py`
- Related baseline docs:
  - `docs/net/network_stack_contract_v1.md`
  - `docs/net/tcp_state_machine_v1.md`
