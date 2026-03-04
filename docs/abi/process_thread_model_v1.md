# Process and Thread Model v1

## Lane

Rugo (Rust no_std kernel). This model applies to the Rugo lane only.

## Status

Compatibility Profile v1 process/runtime baseline established in M8 PR-2 on
2026-03-04.

## Scope

This document defines the v1 contract for:

- ELF64 loader validation policy.
- Startup contract (`argv`/`envp` + aux-vector baseline).
- Process exit/wait semantics.
- File descriptor table v1 semantics.
- Poll/wait baseline behavior.

## ELF loader policy v1

### Accepted object model

- ELF class: `ELF64` only.
- Endianness: little-endian only.
- Program headers required; `PT_LOAD` segments define load map.
- Entry point must be in user address range.

### Segment validation rules

- `p_memsz >= p_filesz` is required.
- `p_align` must be `0` or power-of-two.
- `p_offset + p_filesz` must be within image bounds.
- `p_vaddr + p_memsz` must not overflow and must remain in user range.
- At least one valid `PT_LOAD` segment is required.

### Relocation policy (PR-2 baseline)

- Static, pre-linked images are the supported baseline.
- Dynamic linking and runtime relocation fixups are explicitly unsupported in
  this PR-2 baseline and must fail deterministically.

## Startup contract v1

### `argv`/`envp` delivery

- User entry observes a deterministic startup layout derived from kernel-owned
  argument/environment vectors.
- `argv[argc] == NULL` and `envp[envc] == NULL` are mandatory.
- Strings are copied from kernel-owned startup buffers into user-visible
  startup memory.

### Aux vector baseline

The v1 startup contract includes deterministic aux-vector keys:

- `AT_PHDR`
- `AT_PHENT`
- `AT_PHNUM`
- `AT_PAGESZ` (`4096`)
- `AT_ENTRY`
- `AT_NULL` terminator

## Exit/wait semantics v1

- `_exit`/`exit` transition the calling task to exited state with exit status.
- `wait`/`waitpid` return a deterministic child identifier on success.
- Unsupported pid/options combinations return `-1`.
- If no waitable child event exists, `wait` returns `-1` in the PR-2 baseline.
- When `status_ptr != NULL`, status is copied out through user-pointer
  validation rules (`copyout_user` path).

## File descriptor table v1

### Table shape

- Per-process descriptor table with deterministic slot allocation.
- Slots `0..2` are reserved for stdio-like console behavior.
- New descriptors allocate from lowest available slot `>= 3`.

### Baseline object types in PR-2

- Console descriptor (`/dev/console`).
- Deterministic compatibility file descriptor (`/compat/hello.txt`).

### Syscall behavior

- `open`: returns fd or `-1`.
- `read`: deterministic offset advancement; EOF returns `0`.
- `write`: console write supported; incompatible target returns `-1`.
- `close`: closed/invalid descriptor returns `-1`.
- All pointer-taking paths are validated via `copyin_user`/`copyout_user`.

## Poll baseline semantics v1

- `poll` is the required wait primitive baseline for PR-2.
- `nfds == 0` returns `0`.
- Invalid pointers or malformed descriptor arrays return `-1`.
- Ready count is deterministic for the same table state.

## References

- `docs/abi/syscall_v1.md`
- `docs/abi/compat_profile_v1.md`
- `kernel_rs/src/lib.rs`
