"""M45 PR-1: virtio platform profile v1 report checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_hw_matrix_v6 as matrix  # noqa: E402


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def _out_path(name: str) -> Path:
    path = ROOT / "out" / "pytest-m45" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    return path


def test_hw_matrix_v6_report_is_seed_deterministic():
    first = matrix.run_matrix(seed=20260310)
    second = matrix.run_matrix(seed=20260310)
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_virtio_platform_profile_v1_report_has_profiles_and_bridge():
    out = _out_path("hw-matrix-v6-profile.json")
    rc = matrix.main(["--seed", "20260310", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.hw_matrix_evidence.v6"
    assert data["matrix_contract_id"] == "rugo.hw.support_matrix.v6"
    assert data["virtio_platform_profile_id"] == "rugo.virtio_platform_profile.v1"
    assert data["display_contract_id"] == "rugo.display_stack_contract.v1"
    assert data["shadow_gate"]["baseline_contract_id"] == "rugo.hw.support_matrix.v5"
    assert data["boot_transport_class"] == "virtio-blk-pci-modern"
    assert data["display_class"] == "virtio-gpu-pci"
    assert data["virtio_profile_matrix"]["transitional"]["checks_pass"] is True
    assert data["virtio_profile_matrix"]["modern"]["checks_pass"] is True
    assert (
        data["virtio_profile_matrix"]["transitional"]["storage_device"]
        == "virtio-blk-pci,disable-modern=on"
    )
    assert data["virtio_profile_matrix"]["modern"]["display_device"] == "virtio-gpu-pci"
    assert data["desktop_display_checks"]["bridge_pass"] is True
    assert data["desktop_display_checks"]["display_class"] == "virtio-gpu-pci"
    assert data["desktop_display_checks"]["source_schema"] == "rugo.desktop_smoke_report.v1"
    assert data["shadow_gate"]["promotion_criteria"]["required_green_runs"] == 14
    assert data["gate_pass"] is True


def test_virtio_platform_profile_v1_rejects_unknown_check_id():
    out = _out_path("hw-matrix-v6-profile-error.json")
    rc = matrix.main(
        [
            "--inject-failure",
            "virtio_platform_nonexistent_check",
            "--out",
            str(out),
        ]
    )
    assert rc == 2
    assert not out.exists()
