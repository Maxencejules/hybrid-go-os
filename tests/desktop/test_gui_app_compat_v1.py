"""M35 PR-2: GUI app compatibility matrix checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_gui_app_matrix_v1 as matrix  # noqa: E402


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def test_gui_app_matrix_v1_deterministic():
    first = matrix.run_matrix(seed=20260309)
    second = matrix.run_matrix(seed=20260309)
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_gui_app_matrix_v1_schema_and_gate_pass(tmp_path: Path):
    out = tmp_path / "gui-app-matrix-v1.json"
    rc = matrix.main(["--seed", "20260309", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.gui_app_matrix_report.v1"
    assert data["profile_id"] == "rugo.desktop_profile.v1"
    assert data["tier_schema"] == "rugo.gui_app_tiers.v1"
    assert data["gate_pass"] is True
    assert data["total_failures"] == 0
    assert data["classes"]["productivity"]["meets_threshold"] is True
    assert data["classes"]["media"]["meets_threshold"] is True
    assert data["classes"]["utility"]["meets_threshold"] is True


def test_gui_app_matrix_v1_detects_input_regression(tmp_path: Path):
    out = tmp_path / "gui-app-matrix-v1-fail.json"
    rc = matrix.main(
        [
            "--inject-input-failure",
            "productivity-00",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["total_failures"] >= 1
    assert data["classes"]["productivity"]["meets_threshold"] is False


def test_gui_app_matrix_v1_rejects_unknown_case_id(tmp_path: Path):
    out = tmp_path / "gui-app-matrix-v1-error.json"
    rc = matrix.main(
        [
            "--inject-launch-failure",
            "unknown-case-42",
            "--out",
            str(out),
        ]
    )
    assert rc == 2
    assert not out.exists()

