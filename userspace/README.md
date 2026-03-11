# Userspace Wayfinding

This directory is a stable front-door label for the userspace lane.

Current implementation paths:
- default TinyGo-first userspace: `services/go/`
- experimental stock-Go lane: `services/go_std/`

Important note:
- this directory is wayfinding, not a relocated source tree

Proof paths:
- `make userspace`
- `make image-demo`
- `make boot-demo`
- `python -m pytest tests/go/test_go_user_service.py -v`
- `python -m pytest tests/go/test_std_go_binary.py -v`
