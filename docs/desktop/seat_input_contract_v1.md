# Seat Input Contract v1

Date: 2026-03-11  
Milestone: M49 Input + Seat Management v1  
Status: active release gate

## Objective

Define the first live seat runtime for graphical keyboard and pointer delivery,
including seat ownership, focus-bound routing, and hotplug recovery rules.

## Contract identifiers

- Seat input contract ID: `rugo.seat_input_contract.v1`.
- Parent display runtime contract ID: `rugo.display_runtime_contract.v1`.
- Parent input stack contract ID: `rugo.input_stack_contract.v1`.
- Runtime report schema: `rugo.input_seat_runtime_report.v1`.
- HID event-path schema: `rugo.hid_event_path_report.v1`.
- Input event contract ID: `rugo.input_event_contract.v1`.
- Focus routing policy ID: `rugo.focus_routing_policy.v1`.

## Declared seat model

- Declared seat ID: `seat0`.
- Seat model: single local keyboard/pointer seat.
- Display dependency:
  - source contract: `rugo.display_runtime_contract.v1`
  - active display path comes from `out/input-seat-v1.json`
- Declared input device class: `usb-hid`.
- Declared HID runtime driver: `xhci-usb-hid`.
- Bounded scope:
  - one keyboard path
  - one pointer path
  - one active focus owner
  - one hotplug recovery path for the declared seat

## Required checks

- `keyboard_event_delivery`:
  - focused surface delivery ratio must remain `>= 0.999`.
- `keyboard_repeat_cadence`:
  - keyboard repeat jitter p95 must remain `<= 3 ms`.
- `pointer_motion_delivery`:
  - pointer motion latency p95 must remain `<= 10 ms`.
- `pointer_button_delivery`:
  - pointer button latency p95 must remain `<= 12 ms`.
- `event_sequence_integrity`:
  - reordered input events must remain `= 0`.
- `focus_route_integrity`:
  - focus misroutes must remain `= 0`.
- `focus_transition_budget`:
  - focus transition latency must remain `<= 35 ms`.
- `seat_owner_exclusivity`:
  - exactly one focus owner must exist for `seat0`.
- `seat_hotplug_rebind`:
  - HID device rebind latency must remain `<= 120 ms`.
- `seat_hotplug_recovery`:
  - dropped events during rebind must remain `<= 1`.
- `display_runtime_live`:
  - live graphical display evidence must remain present.
- `usb_hid_declared_support`:
  - declared `usb-hid` focus-capable support must remain present.

## Runtime reporting requirements

- `out/input-seat-v1.json` must expose:
  - `seat`
  - `keyboard`
  - `pointer`
  - `focus`
  - `hotplug`
  - `source_reports`
  - `digest`
- The runtime report must record:
  - `seat_id`
  - `active_display_path`
  - `focus_owner`
  - `focus_owner_count`
  - `total_failures`
  - `gate_pass`
- `out/hid-event-path-v1.json` must remain tied to the runtime report digest and
  active seat state before it can claim `gate_pass=true`.

## Release gating

- Local gate: `make test-input-seat-v1`.
- Local sub-gate: `make test-hid-event-path-v1`.
- CI gate: `Input seat v1 gate`.
- CI sub-gate: `HID event path v1 gate`.
