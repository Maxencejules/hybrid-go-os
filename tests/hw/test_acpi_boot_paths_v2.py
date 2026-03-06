"""M15 acceptance: ACPI/UEFI boot-path hardening checks for matrix v2."""

from pathlib import Path

import pytest


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (_repo_root() / relpath).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "fixture_name,machine",
    [
        ("qemu_serial_blk_q35", "q35"),
        ("qemu_serial_blk_i440fx", "pc/i440fx"),
    ],
)
def test_firmware_boot_paths_remain_deterministic(request, fixture_name, machine):
    """Tiered machine classes must keep deterministic boot/halt markers."""
    out = request.getfixturevalue(fixture_name).stdout
    assert "RUGO: boot ok" in out, (
        f"{machine} missing deterministic boot marker. Got:\n{out}"
    )
    assert "RUGO: halt ok" in out, (
        f"{machine} missing deterministic halt marker. Got:\n{out}"
    )


def test_acpi_uefi_hardening_contract_v2():
    """Firmware hardening doc must include strict validation/fallback rules."""
    hardening = _read("docs/hw/acpi_uefi_hardening_v2.md")
    for token in [
        "`RSDP`",
        "`XSDT`",
        "checksum",
        "safe fallback path",
        "deterministic",
    ]:
        assert token in hardening
