# TCP State Machine v1

Date: 2026-03-04  
Milestone: M12 Network Stack v1

## Purpose

Define the TCP state transition baseline required by M12.

## Required states

- `CLOSED`
- `LISTEN`
- `SYN_SENT`
- `SYN_RECEIVED`
- `ESTABLISHED`
- `FIN_WAIT_1`
- `FIN_WAIT_2`
- `CLOSE_WAIT`
- `LAST_ACK`
- `TIME_WAIT`

## Required transition baseline

- Active open:
  - `CLOSED -> SYN_SENT -> ESTABLISHED`
- Passive open:
  - `LISTEN -> SYN_RECEIVED -> ESTABLISHED`
- Graceful close:
  - `ESTABLISHED -> FIN_WAIT_1 -> FIN_WAIT_2 -> TIME_WAIT -> CLOSED`
- Peer-first close:
  - `ESTABLISHED -> CLOSE_WAIT -> LAST_ACK -> CLOSED`

## Reset and invalid transition behavior

- `RST` on established connection must force deterministic close behavior.
- Invalid transition attempts must fail deterministically (`E_INVAL`/`E_UNSUP`)
  without corrupting connection state.

## Observability requirements

- State transitions must be traceable in deterministic artifacts.
- Retransmission timeout interactions follow:
  - `docs/net/retransmission_timer_policy_v1.md`

## Evidence

- `tests/net/test_tcp_state_machine_v1.py`
- `tests/net/test_tcp_retransmission_v1.py`
