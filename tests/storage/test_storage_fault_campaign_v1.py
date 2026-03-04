"""M13 acceptance: storage fault campaign report."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(ROOT / "tools"))
import run_storage_fault_campaign_v1 as campaign  # noqa: E402


def test_storage_fault_campaign_report_schema_and_threshold():
    max_failures = 0
    data = campaign.run_campaign(seed=20260304, iterations=700)
    data["max_failures"] = max_failures
    data["meets_target"] = data["total_failures"] <= max_failures
    assert data["schema"] == "rugo.storage_fault_campaign_report.v1"
    assert data["iterations"] == 700
    assert data["total_failures"] == 0
    assert data["meets_target"] is True
    assert data["recovered_cases"] >= 0
