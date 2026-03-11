# Kernel Wayfinding

This directory is a stable front-door label for the kernel lane.

Current implementation paths:
- `arch/`
- `boot/`
- `kernel_rs/src/`

Important note:
- this directory is wayfinding, not a second build root
- the real kernel source still lives in the paths above until the repo is
  physically migrated

Proof paths:
- `make kernel`
- `make image-kernel`
- `make boot-kernel`
- `python -m pytest tests/boot tests/trap tests/user tests/ipc tests/drivers -v`
