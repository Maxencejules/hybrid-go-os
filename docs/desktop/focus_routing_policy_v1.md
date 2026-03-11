# Focus Routing Policy v1

Date: 2026-03-11  
Milestone: M49 Input + Seat Management v1  
Status: active release gate

## Objective

Define deterministic focus ownership and routing rules for the first graphical
seat runtime.

## Policy identifiers

- Focus routing policy ID: `rugo.focus_routing_policy.v1`.
- Parent seat contract ID: `rugo.seat_input_contract.v1`.
- Runtime report schema: `rugo.input_seat_runtime_report.v1`.
- HID event-path schema: `rugo.hid_event_path_report.v1`.

## Focus ownership rules

- Only one focus owner may exist per seat.
- `seat0` starts from `desktop.shell.launcher`.
- The declared focus target after settings activation is `settings.panel`.
- Keyboard delivery follows the logical focus owner.
- Pointer delivery follows the hit-tested surface unless capture is active.
- Focus transitions are permitted on pointer button activation and explicit
  keyboard activation only.

## Required routing checks

- `focus_route_integrity` must remain `0` misroutes.
- `focus_transition_budget` must remain `<= 35 ms`.
- `seat_owner_exclusivity` must preserve exactly one focus owner for `seat0`.
- `seat_hotplug_recovery` must restore the pre-hotplug focus owner or the
  current focused surface without introducing a misroute.

## Audit requirements

- The runtime report must expose:
  - `previous_focus_target`
  - `keyboard_focus_target`
  - `pointer_focus_target`
  - `transitions`
  - `misroutes`
- The HID event-path report must expose the focus target before and after the
  focus-changing pointer event.

## Gate anchors

- Local gate: `make test-input-seat-v1`.
- Local sub-gate: `make test-hid-event-path-v1`.
- CI gate: `Input seat v1 gate`.
- CI sub-gate: `HID event path v1 gate`.
