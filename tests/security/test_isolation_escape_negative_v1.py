"""M42 PR-2: deterministic isolation escape negative-path checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_isolation_campaign_v1 as isolation  # noqa: E402


def _check(data: dict, check_id: str) -> dict:
    rows = [entry for entry in data["checks"] if entry["check_id"] == check_id]
    assert len(rows) == 1
    return rows[0]


def test_escape_negative_paths_pass_in_campaign():
    report = isolation.run_campaign(seed=20260310)
    assert report["summary"]["escape"]["pass"] is True
    assert report["escape_negative_paths"]["setns_denied_ratio"] == 1.0
    assert report["escape_negative_paths"]["cross_tenant_signal_denied_ratio"] == 1.0
    assert report["escape_negative_paths"]["mount_propagation_block_ratio"] == 1.0
    assert report["escape_negative_paths"]["privilege_escalation_events"] == 0
    assert report["escape_negative_paths"]["namespace_leak_events"] == 0
    assert _check(report, "escape_setns_denied_ratio")["pass"] is True
    assert _check(report, "escape_cross_tenant_signal_denied_ratio")["pass"] is True
    assert _check(report, "escape_mount_propagation_block_ratio")["pass"] is True
    assert _check(report, "escape_privilege_escalation_events")["pass"] is True


def test_escape_negative_paths_detect_regression(tmp_path: Path):
    out = tmp_path / "isolation-campaign-v1-escape-fail.json"
    rc = isolation.main(
        [
            "--inject-failure",
            "escape_setns_denied_ratio",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["escape"]["failures"] >= 1
    assert _check(data, "escape_setns_denied_ratio")["pass"] is False
