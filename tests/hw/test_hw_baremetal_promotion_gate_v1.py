"""M37 aggregate sub-gate: bare-metal promotion v1 wiring and artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import collect_hw_promotion_evidence_v1 as promotion  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_hw_baremetal_promotion_gate_v1_wiring_and_artifacts(tmp_path: Path):
    required = [
        "docs/M37_EXECUTION_BACKLOG.md",
        "docs/hw/support_matrix_v4.md",
        "docs/hw/bare_metal_promotion_policy_v1.md",
        "tools/collect_hw_promotion_evidence_v1.py",
        "tests/hw/test_baremetal_promotion_v1.py",
        "tests/hw/test_hw_baremetal_promotion_gate_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M37 promotion artifact: {rel}"

    roadmap = _read("docs/M35_M39_GENERAL_PURPOSE_EXPANSION_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M37_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-hw-baremetal-promotion-v1" in roadmap

    assert "test-hw-baremetal-promotion-v1" in makefile
    for entry in [
        "tools/collect_hw_promotion_evidence_v1.py --out $(OUT)/hw-promotion-v1.json",
        "tests/hw/test_baremetal_promotion_v1.py",
        "tests/hw/test_hw_baremetal_promotion_gate_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-hw-baremetal-promotion-v1.xml" in makefile

    assert "Hardware bare-metal promotion v1 gate" in ci
    assert "make test-hw-baremetal-promotion-v1" in ci
    assert "hw-baremetal-promotion-v1-artifacts" in ci
    assert "out/pytest-hw-baremetal-promotion-v1.xml" in ci
    assert "out/hw-promotion-v1.json" in ci

    assert "Status: done" in backlog
    assert "M37" in milestones
    assert "M37" in status
    assert "docs/architecture/SOURCE_MAP.md" in readme
    assert "docs/archive/README.md" in readme

    out = tmp_path / "hw-promotion-v1.json"
    assert promotion.main(["--seed", "20260309", "--out", str(out)]) == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["schema"] == "rugo.hw_baremetal_promotion_report.v1"
    assert report["policy_id"] == "rugo.hw_baremetal_promotion_policy.v1"
    assert report["gate_pass"] is True
    assert report["total_failures"] == 0
