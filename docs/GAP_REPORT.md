# G2 Gap Report (Rugo Lane)

- [x] **P1 - Unified user-copy is applied to pointer syscalls (resolved 2026-03-02)**: `sys_debug_write`, `sys_blk_read`, `sys_blk_write`, `sys_net_send`, and `sys_net_recv` use the shared `copyin_user`/`copyout_user` path, matching `docs/abi/syscall_v0.md` user-pointer safety requirements.

- [ ] **P2 - IPC semantics still have undefined/silent-overwrite behaviors**: `sys_ipc_recv_r4` stores only one waiter ID per endpoint (`waiter: i32`), so a second waiter can overwrite the first wait registration; `sys_ipc_send_r4` also clamps payload length to 256 bytes. Current acceptance coverage checks occupied-slot behavior (`tests/ipc/test_ipc_buffer_full.py`) but does not cover multi-waiter semantics.

- [ ] **P3 - Service registry endpoint-validity semantics are undefined**: overwrite/full-table mechanics are covered (`tests/ipc/test_svc_overwrite.py`, `tests/ipc/test_svc_full.py`), but `sys_svc_register_r4` stores endpoint IDs without validating endpoint existence/activeness.

- [ ] **P4 - VirtIO blk invariant failure paths are not tested**: init hardening checks exist and `BLK: invariants ok` is tested (`tests/drivers/test_virtio_blk_init_invariants.py`), but failure-path validation for `BLK: init failed` is still missing.

- [x] **P5 - TinyGo dependency contract for full test entrypoint clarified (resolved 2026-03-02)**: `docs/BUILD.md` now states that Go/TinyGo are required for local `make image-go` and full `make test-qemu`, while remaining optional for `make build`/`make image`.
