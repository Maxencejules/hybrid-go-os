# ACPI and UEFI Hardening v2

Date: 2026-03-06  
Milestone: M15  
Lane: Rugo (Rust kernel + Go user space)

## Scope

Define deterministic ACPI and UEFI table-consumption rules for hardware matrix
v2 boot paths.

## Boot-path contract

- Boot remains valid only with deterministic `RUGO: boot ok` and
  `RUGO: halt ok` markers.
- ACPI/UEFI parsing failures must take a safe fallback path.
- Firmware-table errors must not trigger silent continuation.

## Validation invariants

### Identity and structure checks

- Verify table signatures (`RSDP`, `XSDT`, and consumer-specific signatures).
- Validate table `length` before parsing bodies.
- Reject structurally impossible or zero-length headers.

### Integrity checks

- Validate ACPI checksum before use.
- Reject unsupported revisions deterministically.

### Address safety

- Validate pointer bounds, alignment, and overflow.
- Reject out-of-range table pointers with explicit fallback behavior.

## Deterministic failure policy

- Invalid firmware metadata must produce stable diagnostics.
- The kernel must keep control flow deterministic under malformed tables.
- Safe fallback behavior must preserve release-gate checks for supported tiers.

## Cross references

- Matrix policy: `docs/hw/support_matrix_v2.md`
- Device profile contract: `docs/hw/device_profile_contract_v2.md`
- Bring-up runbook: `docs/hw/bare_metal_bringup_v2.md`
