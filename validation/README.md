# Validation Wayfinding

This directory names the validation surface without moving existing test paths.

Current implementation path:
- `tests/`

Validation categories:
- live QEMU/runtime proofs
- contract and doc checks
- aggregate gate wiring

Important note:
- many later qualification gates rely on deterministic report generators under
  `tools/`
- treat those as validation scaffolding around the runtime, not as new runtime
  subsystems
