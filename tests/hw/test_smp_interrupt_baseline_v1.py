"""M43 PR-2: deterministic SMP interrupt baseline v1 checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import collect_firmware_smp_evidence_v1 as evidence  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _policy_check(data: dict, check_id: str) -> dict:
    rows = [entry for entry in data["policy_checks"] if entry["check_id"] == check_id]
    assert len(rows) == 1
    return rows[0]


def test_smp_interrupt_model_v1_doc_declares_required_tokens():
    model = _read("docs/runtime/smp_interrupt_model_v1.md")
    for token in [
        "SMP interrupt model ID: `rugo.smp_interrupt_model.v1`.",
        "Matrix evidence schema: `rugo.hw_matrix_evidence.v5`.",
        "Firmware evidence schema: `rugo.hw_firmware_smp_evidence.v1`.",
        "`bootstrap_cpu_online_ratio`",
        "`application_cpu_online_ratio`",
        "`ipi_roundtrip_p95_ms`",
        "`lost_interrupt_events`",
        "`spurious_interrupt_rate`",
    ]:
        assert token in model


def test_smp_interrupt_baseline_v1_schema_and_pass(tmp_path: Path):
    out = tmp_path / "hw-firmware-smp-v1-smp.json"
    rc = evidence.main(["--seed", "20260310", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.hw_firmware_smp_evidence.v1"
    assert data["smp_interrupt_model_id"] == "rugo.smp_interrupt_model.v1"
    assert data["gate_pass"] is True
    assert data["smp_baseline"]["checks_pass"] is True
    assert data["smp_baseline"]["bootstrap_cpu_online_ratio"] >= 1.0
    assert data["smp_baseline"]["application_cpu_online_ratio"] >= 0.99
    assert data["smp_baseline"]["ipi_roundtrip_p95_ms"] <= 4.0
    assert data["smp_baseline"]["lost_interrupt_events"] == 0
    assert data["smp_baseline"]["spurious_interrupt_rate"] <= 0.01
    assert _policy_check(data, "smp_checks_pass")["pass"] is True
    assert _policy_check(data, "no_lost_interrupts")["pass"] is True


def test_smp_interrupt_baseline_v1_detects_lost_interrupt_regression(tmp_path: Path):
    out = tmp_path / "hw-firmware-smp-v1-smp-fail.json"
    rc = evidence.main(
        [
            "--inject-failure",
            "smp_lost_interrupt_events",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["smp_baseline"]["checks_pass"] is False
    assert data["smp_baseline"]["lost_interrupt_events"] > 0
    assert _policy_check(data, "smp_checks_pass")["pass"] is False
    assert _policy_check(data, "no_lost_interrupts")["pass"] is False


def test_smp_interrupt_baseline_v1_detects_ipi_budget_regression(tmp_path: Path):
    out = tmp_path / "hw-firmware-smp-v1-smp-ipi-fail.json"
    rc = evidence.main(
        [
            "--inject-failure",
            "smp_ipi_roundtrip_p95_ms",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["smp_baseline"]["checks_pass"] is False
    assert data["smp_baseline"]["ipi_roundtrip_p95_ms"] > 4.0
    assert _policy_check(data, "ipi_roundtrip_budget")["pass"] is False
