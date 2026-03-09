"""M39 PR-2: deterministic app catalog simulation checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_app_catalog_sim_v1 as sim  # noqa: E402


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def _check(data: dict, check_id: str) -> dict:
    rows = [entry for entry in data["checks"] if entry["check_id"] == check_id]
    assert len(rows) == 1
    return rows[0]


def test_app_catalog_sim_v1_report_is_seed_deterministic():
    first = sim.run_simulation(seed=20260309)
    second = sim.run_simulation(seed=20260309)
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_app_catalog_sim_v1_schema_and_pass(tmp_path: Path):
    out = tmp_path / "app-catalog-sim-v1.json"
    rc = sim.main(["--seed", "20260309", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.app_catalog_sim_report.v1"
    assert data["ecosystem_policy_id"] == "rugo.ecosystem_scale_policy.v1"
    assert data["catalog_quality_contract_id"] == "rugo.catalog_quality_contract.v1"
    assert data["distribution_workflow_id"] == "rugo.distribution_workflow.v1"
    assert data["gate_pass"] is True
    assert data["total_failures"] == 0
    assert data["summary"]["coverage"]["pass"] is True
    assert data["summary"]["quality"]["pass"] is True
    assert data["summary"]["reproducibility"]["pass"] is True
    assert data["catalog"]["catalog_total_entries"] >= 420
    assert data["catalog"]["class_counts"]["productivity"] >= 120
    assert data["catalog"]["class_counts"]["devtools"] >= 90
    assert data["catalog"]["class_counts"]["media"] >= 70
    assert data["catalog"]["class_counts"]["utility"] >= 140
    assert data["quality"]["metadata_completeness_ratio"] >= 0.995
    assert data["quality"]["signed_provenance_ratio"] >= 1.0
    assert data["quality"]["unsupported_workload_ratio"] <= 0.02
    assert data["quality"]["policy_violation_count"] == 0
    assert _check(data, "catalog_total_entries")["pass"] is True
    assert _check(data, "index_rebuild_determinism_ratio")["pass"] is True


def test_app_catalog_sim_v1_detects_catalog_size_regression(tmp_path: Path):
    out = tmp_path / "app-catalog-sim-v1-fail.json"
    rc = sim.main(
        [
            "--inject-failure",
            "catalog_total_entries",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["coverage"]["failures"] >= 1
    assert _check(data, "catalog_total_entries")["pass"] is False


def test_app_catalog_sim_v1_rejects_unknown_check_id(tmp_path: Path):
    out = tmp_path / "app-catalog-sim-v1-error.json"
    rc = sim.main(
        [
            "--inject-failure",
            "catalog_nonexistent_check",
            "--out",
            str(out),
        ]
    )
    assert rc == 2
    assert not out.exists()
