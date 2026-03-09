"""M28 PR-2: deterministic security fuzz v2 tooling checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_security_fuzz_v2 as fuzz_tool  # noqa: E402


def _strip_timestamp(payload: dict) -> dict:
    stable = dict(payload)
    stable.pop("created_utc", None)
    return stable


def test_security_fuzz_v2_is_seed_deterministic():
    first = fuzz_tool.run_campaign(seed=20260309, iterations=320, cases=5)
    second = fuzz_tool.run_campaign(seed=20260309, iterations=320, cases=5)
    assert _strip_timestamp(first) == _strip_timestamp(second)


def test_security_fuzz_v2_report_schema_and_pass(tmp_path: Path):
    out = tmp_path / "security-fuzz-v2.json"
    rc = fuzz_tool.main(
        [
            "--seed",
            "20260309",
            "--iterations",
            "600",
            "--cases",
            "5",
            "--max-violations",
            "0",
            "--out",
            str(out),
        ]
    )
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.security_fuzz_report.v2"
    assert data["campaign_id"] == "rugo.security_fuzz_campaign.v2"
    assert data["profile_id"] == "rugo.security_hardening_profile.v3"
    assert data["total_violations"] == 0
    assert data["gate_pass"] is True
    assert data["closure_sla_hours"] == 24


def test_security_fuzz_v2_detects_injected_violation(tmp_path: Path):
    out = tmp_path / "security-fuzz-v2.json"
    rc = fuzz_tool.main(
        [
            "--seed",
            "20260309",
            "--iterations",
            "400",
            "--cases",
            "5",
            "--inject-violation",
            "rights_downgrade_only",
            "--max-violations",
            "0",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.security_fuzz_report.v2"
    assert data["total_violations"] >= 1
    assert data["gate_pass"] is False
    assert any(
        case["name"] == "rights_downgrade_only" and case["pass"] is False
        for case in data["results"]
    )
