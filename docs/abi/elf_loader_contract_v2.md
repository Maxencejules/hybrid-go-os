# ELF Loader Contract v2

## Lane

Rugo (Rust `no_std` kernel), Compatibility Profile v2.

## Status

Active in M17 (2026-03-06).

## Contract identity

Loader contract identifier: `rugo.elf_loader_contract.v2`.

## Scope

This document defines deterministic loader behavior for:

- static ELF (`ET_EXEC`) payloads,
- dynamic ELF (`ET_DYN`) payloads with bounded relocation behavior.

## Accepted object classes

- ELF class: 64-bit only.
- Endianness: little-endian only.
- User entry and mapped segments must remain below user virtual limit.
- At least one valid `PT_LOAD` segment is required.

## Static path (`ET_EXEC`)

Static ELF is accepted when all segment bounds checks pass and no dynamic
relocation pipeline is required.

## Dynamic path (`ET_DYN`)

Dynamic ELF (`ET_DYN`) is accepted when interpreter and relocation constraints
are met.

Required constraints:

- Interpreter must be explicit and supported: `/lib/rugo-ld.so.1`.
- Dynamic relocation count must be bounded.
- Relocation target addresses must lie inside mapped user segments.
- Relocation ordering must be deterministic for equivalent input images.

## Relocation support policy

Only `R_X86_64_RELATIVE` relocations are supported.

Unsupported relocation kinds must fail with deterministic unsupported error.
Missing interpreter data for dynamic payloads must fail deterministically.

## Deterministic failure policy

The loader must reject malformed images without partial state mutation.

Contract-level failure classes:

- `E_INVAL`: malformed headers/segment shape errors.
- `E_RANGE`: relocation count/range limit violations.
- `E_FAULT`: relocation target outside mapped user range.
- `E_UNSUP`: unsupported interpreter or relocation kind.

## Startup handoff constraints

- Aux-vector keys remain consistent with v1 baseline (`AT_PHDR`, `AT_PHENT`,
  `AT_PHNUM`, `AT_PAGESZ`, `AT_ENTRY`, `AT_NULL`).
- Startup contract remains deterministic for equivalent image + argv/envp input.

## Conformance references

- `tests/compat/v2_model.py`
- `tests/compat/test_elf_loader_dynamic_v2.py`
- `tests/compat/test_abi_profile_v2_docs.py`
- `kernel_rs/src/lib.rs` (current loader baseline entry point:
  `elf_v1_validate_image`)

