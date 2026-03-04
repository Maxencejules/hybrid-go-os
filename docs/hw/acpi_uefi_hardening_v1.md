# ACPI and UEFI Hardening v1

Date: 2026-03-04  
Milestone: M9

## Scope

Define firmware-table handling rules for ACPI/UEFI-derived data that the
kernel or early boot code may consume.

Boot transport is mediated by Limine. The hardening goal is deterministic
validation before any table-driven behavior is trusted.

## Validation policy

### Table identity and length

- Validate signature before parsing table body.
- Validate reported table length against accessible memory range.
- Reject zero-length or structurally impossible tables.

### Checksum and revision

- Verify ACPI checksum before table use.
- Enforce minimum revision requirements per table consumer.
- Reject unsupported revisions deterministically.

### Pointer and alignment safety

- Validate pointer alignment and overflow on pointer arithmetic.
- Reject table pointers that resolve outside expected memory map ranges.

### Deterministic failure

- Invalid table inputs must produce stable diagnostics and a safe fallback path.
- Table parsing must never panic or silently continue on malformed data.

## v1 deliverables in M9

- Hardening contract captured in this document.
- Hardware matrix and bring-up workflows require serial diagnostics collection
  for firmware-identification and early-device probe behavior.
- Bare-metal runbook defines minimum evidence set before promoting a board from
  exploratory status.

## Follow-on implementation hooks

The following are tracked as post-v1 implementation tasks:

- Add explicit ACPI table parser modules with checksum-enforced decode.
- Add table-fuzz tests for malformed headers and length overflows.
- Add UEFI handoff diagnostics markers to the boot report path.

## Non-goals for v1

- Full ACPI namespace interpreter.
- Full UEFI runtime services support.
- Power-management policy completeness.
