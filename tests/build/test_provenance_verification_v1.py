"""M31 acceptance: provenance schema verification path."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import generate_provenance_v1 as provenance  # noqa: E402
import generate_sbom_v1 as sbom  # noqa: E402
import verify_sbom_provenance_v2 as verify  # noqa: E402


def test_provenance_verification_v1(tmp_path: Path):
    sbom_out = tmp_path / "sbom-v1.spdx.json"
    prov_out = tmp_path / "provenance-v1.json"
    report_out = tmp_path / "supply-chain-revalidation-v1.json"
    assert sbom.main(["--out", str(sbom_out)]) == 0
    assert provenance.main(["--out", str(prov_out)]) == 0
    assert verify.main(["--sbom", str(sbom_out), "--provenance", str(prov_out), "--out", str(report_out)]) == 0
    data = json.loads(report_out.read_text(encoding="utf-8"))
    checks = {c["name"]: c["pass"] for c in data["checks"]}
    assert checks["provenance_schema"] is True
    assert checks["subject_consistency"] is True

