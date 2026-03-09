"""M37 PR-2: deterministic hardware matrix v4 checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_hw_matrix_v4 as matrix  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _coverage_entry(data: dict, device: str) -> dict:
    rows = [entry for entry in data["device_class_coverage"] if entry["device"] == device]
    assert len(rows) == 1
    return rows[0]


@pytest.mark.parametrize(
    "fixture_name,tier,machine",
    [
        ("qemu_serial_blk_q35", "tier0", "q35"),
        ("qemu_serial_blk_i440fx", "tier1", "pc/i440fx"),
    ],
)
def test_storage_smoke_matrix_v4(request, fixture_name, tier, machine):
    """Tier 0 and Tier 1 must keep deterministic storage probe/rw markers."""
    out = request.getfixturevalue(fixture_name).stdout
    assert "RUGO: boot ok" in out, (
        f"{tier} ({machine}) missing boot marker for v4 matrix run. Got:\n{out}"
    )
    assert "BLK: found virtio-blk" in out, (
        f"{tier} ({machine}) missing storage probe marker for v4. Got:\n{out}"
    )
    assert "BLK: rw ok" in out, (
        f"{tier} ({machine}) missing storage rw marker for v4. Got:\n{out}"
    )


@pytest.mark.parametrize(
    "fixture_name,tier,machine",
    [
        ("qemu_serial_net_q35", "tier0", "q35"),
        ("qemu_serial_net_i440fx", "tier1", "pc/i440fx"),
    ],
)
def test_network_smoke_matrix_v4(request, fixture_name, tier, machine):
    """Tier 0 and Tier 1 must keep deterministic network probe/runtime markers."""
    out = request.getfixturevalue(fixture_name).stdout
    assert "RUGO: boot ok" in out, (
        f"{tier} ({machine}) missing boot marker for v4 matrix run. Got:\n{out}"
    )
    assert "NET: virtio-net ready" in out, (
        f"{tier} ({machine}) missing network ready marker for v4. Got:\n{out}"
    )
    assert "NET: udp echo" in out, (
        f"{tier} ({machine}) missing UDP echo marker for v4. Got:\n{out}"
    )


def test_matrix_v4_contract_and_gate_schema():
    """Support matrix v4 must define tiers, schema, and gate bindings."""
    doc = _read("docs/hw/support_matrix_v4.md")
    for token in [
        "Tier 0",
        "Tier 1",
        "Tier 2",
        "Tier 3",
        "Tier 4",
        "Schema identifier: `rugo.hw_matrix_evidence.v4`",
        "Local gate: `make test-hw-matrix-v4`.",
        "Local sub-gate: `make test-hw-baremetal-promotion-v1`.",
        "Hardware support claims are bounded to matrix v4 evidence only.",
    ]:
        assert token in doc


def test_hw_matrix_v4_report_schema_and_pass(tmp_path: Path):
    out = tmp_path / "hw-matrix-v4.json"
    rc = matrix.main(["--seed", "20260309", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.hw_matrix_evidence.v4"
    assert data["matrix_contract_id"] == "rugo.hw.support_matrix.v4"
    assert data["driver_contract_id"] == "rugo.driver_lifecycle_report.v4"
    assert data["promotion_policy_id"] == "rugo.hw_baremetal_promotion_policy.v1"
    assert data["gate_pass"] is True
    assert data["total_failures"] == 0
    assert data["summary"]["matrix"]["pass"] is True
    assert data["summary"]["coverage"]["pass"] is True
    assert _coverage_entry(data, "ahci")["status"] == "pass"
    assert _coverage_entry(data, "nvme")["status"] == "pass"
    assert _coverage_entry(data, "e1000")["status"] == "pass"
    assert _coverage_entry(data, "rtl8139")["status"] == "pass"


def test_hw_matrix_v4_detects_coverage_regression(tmp_path: Path):
    out = tmp_path / "hw-matrix-v4-coverage-fail.json"
    rc = matrix.main(
        [
            "--inject-failure",
            "coverage_storage_nvme",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["coverage"]["failures"] >= 1
    assert _coverage_entry(data, "nvme")["status"] == "fail"
