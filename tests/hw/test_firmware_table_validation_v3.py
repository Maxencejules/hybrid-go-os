"""M43 PR-2: deterministic firmware table validation v3 checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import collect_firmware_smp_evidence_v1 as evidence  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def _policy_check(data: dict, check_id: str) -> dict:
    rows = [entry for entry in data["policy_checks"] if entry["check_id"] == check_id]
    assert len(rows) == 1
    return rows[0]


def test_acpi_uefi_hardening_v3_doc_declares_required_tokens():
    hardening = _read("docs/hw/acpi_uefi_hardening_v3.md")
    for token in [
        "Hardening identifier: `rugo.acpi_uefi_hardening.v3`.",
        "Parent matrix schema: `rugo.hw_matrix_evidence.v5`.",
        "SMP model ID: `rugo.smp_interrupt_model.v1`.",
        "`RSDP`",
        "`XSDT`",
        "`FADT`",
        "`MADT`",
        "`MCFG`",
        "checksum",
        "safe fallback path",
    ]:
        assert token in hardening


def test_firmware_smp_evidence_v1_is_seed_deterministic():
    first = evidence.run_collection(seed=20260310)
    second = evidence.run_collection(seed=20260310)
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_firmware_table_validation_v3_schema_and_pass(tmp_path: Path):
    out = tmp_path / "hw-firmware-smp-v1-firmware.json"
    rc = evidence.main(["--seed", "20260310", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.hw_firmware_smp_evidence.v1"
    assert data["firmware_hardening_id"] == "rugo.acpi_uefi_hardening.v3"
    assert data["matrix_schema_id"] == "rugo.hw_matrix_evidence.v5"
    assert data["gate_pass"] is True
    assert data["firmware_table_validation"]["checks_pass"] is True
    assert data["firmware_table_validation"]["rsdp_checksum_pass"] is True
    assert data["firmware_table_validation"]["xsdt_parse_pass"] is True
    assert data["firmware_table_validation"]["madt_topology_pass"] is True
    assert "MADT" in data["firmware_table_validation"]["signatures"]
    assert _policy_check(data, "firmware_checks_pass")["pass"] is True


def test_firmware_table_validation_v3_detects_madt_regression(tmp_path: Path):
    out = tmp_path / "hw-firmware-smp-v1-firmware-fail.json"
    rc = evidence.main(
        [
            "--inject-failure",
            "firmware_madt_topology",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["firmware_table_validation"]["madt_topology_pass"] is False
    assert _policy_check(data, "firmware_checks_pass")["pass"] is False


def test_firmware_table_validation_v3_rejects_unknown_check_id(tmp_path: Path):
    out = tmp_path / "hw-firmware-smp-v1-firmware-error.json"
    rc = evidence.main(
        [
            "--inject-failure",
            "firmware_nonexistent_check",
            "--out",
            str(out),
        ]
    )
    assert rc == 2
    assert not out.exists()
