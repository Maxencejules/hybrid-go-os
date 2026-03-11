# Input Event Contract v1

Date: 2026-03-11  
Milestone: M49 Input + Seat Management v1  
Status: active release gate

## Objective

Define the ordered event phases and delivery metadata required for the first
live keyboard and pointer seat runtime.

## Contract identifiers

- Input event contract ID: `rugo.input_event_contract.v1`.
- Parent seat contract ID: `rugo.seat_input_contract.v1`.
- Runtime report schema: `rugo.input_seat_runtime_report.v1`.
- HID event-path schema: `rugo.hid_event_path_report.v1`.

## Required keyboard phases

- Required keyboard phases: `key_down`, `key_repeat`, `key_up`.
- Required keyboard metadata:
  - `seq`
  - `seat_id`
  - `device_id`
  - `target`
  - `focus_owner`

## Required pointer phases

- Required pointer phases: `pointer_motion`, `button_down`, `button_up`.
- Required pointer metadata:
  - `seq`
  - `seat_id`
  - `device_id`
  - `target`
  - `focus_before`
  - `focus_after`

## Ordered delivery rules

- Event sequence numbers must increase monotonically within one event-path
  report.
- `event_sequence_integrity` is release-blocking.
- Keyboard delivery must follow the runtime focus owner.
- Pointer button delivery may update focus and must emit the post-route target.
- `pointer_button_delivery` remains release-blocking.
- Hotplug transitions must emit `device_detach` followed by `device_rebind`
  before pointer delivery can resume.

## Report anchors

- `out/hid-event-path-v1.json` must expose:
  - `event_stream`
  - `event_counts`
  - `keyboard_path`
  - `pointer_path`
  - `focus_path`
  - `hotplug_path`
  - `sequence_sha256`
- The event-path report must reference the runtime digest from
  `out/input-seat-v1.json`.
