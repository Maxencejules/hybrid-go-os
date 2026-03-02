# Screenshot and GIF capture recipe

This folder stores real captures only. Do not commit synthetic images.

## Fixed capture profile

- Output resolution: `1280x720`
- Terminal size: `120 columns x 36 rows`
- Serial console must be visible (`RUGO:` markers readable)
- Keep one consistent terminal theme/font across captures

## Canonical commands

1. `make image`
2. `make run` (boot screenshot source)
3. `make test-qemu` (optional GIF source)

These paths are canonical in this repo:
- `tools/run_qemu.sh` (`make run`)
- `tests/conftest.py` (`make test-qemu` harness)

Both rely on serial output (`-serial stdio`). Capture the terminal running the command.

## Boot screenshot steps

1. Resize terminal to `120x36`.
2. Run `make run`.
3. Wait until `RUGO: boot ok` and `RUGO: halt ok` are visible.
4. Capture a `1280x720` image.
5. Save as `boot-qemu.png`.

## GIF steps (10 to 20 seconds)

1. Resize terminal to `120x36`.
2. Start screen recording at `1280x720`.
3. Run `make run` or `make test-qemu`.
4. Stop recording between 10 and 20 seconds.
5. Export as `make-run-demo.gif` or `make-test-qemu-demo.gif`.

## Redaction rules

Blur only host-specific data if it appears:
- local username/home path segments
- local hostnames or IPs unrelated to OS behavior
- unrelated terminal tabs/windows

Do not blur:
- repo paths and commands
- QEMU flags used by this project
- test/kernel markers such as `RUGO: ...`, `NET: udp echo`, `GOUSR: ok`

## File naming conventions

- Screenshots: `<topic>-qemu.png`
- GIFs: `<command>-demo.gif`
- Use lowercase kebab-case only
