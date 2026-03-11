"""M37 aggregate gate: hardware matrix v4 wiring and closure checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import collect_hw_promotion_evidence_v1 as promotion  # noqa: E402
import run_hw_matrix_v4 as matrix  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_hw_matrix_v4_gate_wiring_and_artifacts(tmp_path: Path):
    required = [
        "docs/M37_EXECUTION_BACKLOG.md",
        "docs/hw/support_matrix_v4.md",
        "docs/hw/driver_lifecycle_contract_v4.md",
        "docs/hw/bare_metal_promotion_policy_v1.md",
        "tools/run_hw_matrix_v4.py",
        "tools/collect_hw_promotion_evidence_v1.py",
        "tests/hw/test_hw_matrix_docs_v4.py",
        "tests/hw/test_hw_matrix_v4.py",
        "tests/hw/test_driver_lifecycle_v4.py",
        "tests/hw/test_baremetal_promotion_v1.py",
        "tests/hw/test_hw_negative_paths_v4.py",
        "tests/hw/test_hw_baremetal_promotion_gate_v1.py",
        "tests/hw/test_hw_gate_v4.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M37 artifact: {rel}"

    roadmap = _read("docs/M35_M39_GENERAL_PURPOSE_EXPANSION_ROADMAP.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    backlog = _read("docs/M37_EXECUTION_BACKLOG.md")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")
    readme = _read("README.md")

    assert "test-hw-matrix-v4" in roadmap
    assert "test-hw-baremetal-promotion-v1" in roadmap

    assert "test-hw-matrix-v4" in makefile
    for entry in [
        "tools/run_hw_matrix_v4.py --out $(OUT)/hw-matrix-v4.json",
        "$(MAKE) test-hw-baremetal-promotion-v1",
        "tests/hw/test_hw_matrix_docs_v4.py",
        "tests/hw/test_hw_matrix_v4.py",
        "tests/hw/test_driver_lifecycle_v4.py",
        "tests/hw/test_baremetal_promotion_v1.py",
        "tests/hw/test_hw_negative_paths_v4.py",
        "tests/hw/test_hw_gate_v4.py",
    ]:
        assert entry in makefile
    assert "pytest-hw-matrix-v4.xml" in makefile
    assert "pytest-hw-baremetal-promotion-v1.xml" in makefile

    assert "Hardware matrix v4 gate" in ci
    assert "make test-hw-matrix-v4" in ci
    assert "hw-matrix-v4-artifacts" in ci
    assert "out/pytest-hw-matrix-v4.xml" in ci
    assert "out/hw-matrix-v4.json" in ci

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

    matrix_out = tmp_path / "hw-matrix-v4.json"
    promo_out = tmp_path / "hw-promotion-v1.json"

    assert matrix.main(["--seed", "20260309", "--out", str(matrix_out)]) == 0
    assert promotion.main(["--seed", "20260309", "--out", str(promo_out)]) == 0

    matrix_data = json.loads(matrix_out.read_text(encoding="utf-8"))
    promo_data = json.loads(promo_out.read_text(encoding="utf-8"))

    assert matrix_data["schema"] == "rugo.hw_matrix_evidence.v4"
    assert matrix_data["gate_pass"] is True
    assert matrix_data["total_failures"] == 0

    assert promo_data["schema"] == "rugo.hw_baremetal_promotion_report.v1"
    assert promo_data["policy_id"] == "rugo.hw_baremetal_promotion_policy.v1"
    assert promo_data["gate_pass"] is True
