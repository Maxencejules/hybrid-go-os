# ACPI and UEFI Hardening v3

Date: 2026-03-10  
Milestone: M43 Hardware/Firmware Breadth + SMP v1  
Lane: Rugo (Rust kernel + Go user space)  
Status: active contract

## Scope

Define deterministic ACPI and UEFI table-consumption rules for matrix v5 and
SMP interrupt/topology baseline checks.

## Contract identities

- Hardening identifier: `rugo.acpi_uefi_hardening.v3`.
- Parent matrix schema: `rugo.hw_matrix_evidence.v5`.
- SMP model ID: `rugo.smp_interrupt_model.v1`.
- Firmware evidence schema: `rugo.hw_firmware_smp_evidence.v1`.

## Boot-path contract

- Boot remains valid only with deterministic `RUGO: boot ok` and
  `RUGO: halt ok` markers.
- ACPI/UEFI parsing failures must take a safe fallback path.
- Firmware-table errors must not trigger silent continuation.

## Validation invariants

### Identity and structure checks

- Verify table signatures (`RSDP`, `XSDT`, `FADT`, `MADT`, `MCFG`).
- Validate table `length` before parsing bodies.
- Reject structurally impossible or zero-length headers.

### Integrity checks

- Validate ACPI checksum before use.
- Reject unsupported revisions deterministically.

### Address safety

- Validate pointer bounds, alignment, and overflow.
- Reject out-of-range table pointers with explicit fallback behavior.

### SMP topology safety

- Validate `MADT` LAPIC entry uniqueness and non-zero CPU-count invariants.
- Reject duplicate APIC IDs and inconsistent enabled/disabled flags.
- Keep interrupt-routing fallbacks deterministic when firmware topology is
  incomplete.

## Deterministic failure policy

- Invalid firmware metadata must produce stable diagnostics.
- The kernel must keep control flow deterministic under malformed tables.
- Safe fallback behavior must preserve release-gate checks for supported tiers.

## Gate binding

- Local gate: `make test-hw-firmware-smp-v1`.
- Local sub-gate: `make test-native-driver-matrix-v1`.
- CI gate: `Hardware firmware smp v1 gate`.
- CI sub-gate: `Native driver matrix v1 gate`.

## Cross references

- Matrix policy: `docs/hw/support_matrix_v5.md`
- Driver lifecycle contract: `docs/hw/driver_lifecycle_contract_v5.md`
- SMP interrupt model: `docs/runtime/smp_interrupt_model_v1.md`
