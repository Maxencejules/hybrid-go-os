# Crash Dump Contract v1

Status: draft  
Version: v1

## Objective

Define panic-to-dump artifact requirements for deterministic postmortem analysis.

## Contract

- Panic event emits a machine-readable dump.
- Dump includes panic code, register set, and stack frame list.
- Dump schema version is pinned and backward-compatible within v1 window.

## Evidence

- Dump schema: `rugo.crash_dump.v1`.
- Symbolized schema: `rugo.crash_dump_symbolized.v1`.

