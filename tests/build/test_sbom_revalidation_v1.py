"""M31 acceptance: SBOM/provenance revalidation baseline."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import generate_provenance_v1 as provenance  # noqa: E402
import generate_sbom_v1 as sbom  # noqa: E402
import verify_sbom_provenance_v2 as verify  # noqa: E402


def test_sbom_revalidation_v1(tmp_path: Path):
    sbom_out = tmp_path / "sbom-v1.spdx.json"
    prov_out = tmp_path / "provenance-v1.json"
    report_out = tmp_path / "supply-chain-revalidation-v1.json"
    assert sbom.main(["--out", str(sbom_out)]) == 0
    assert provenance.main(["--out", str(prov_out)]) == 0
    assert (
        verify.main(
            [
                "--sbom",
                str(sbom_out),
                "--provenance",
                str(prov_out),
                "--out",
                str(report_out),
                "--max-failures",
                "0",
            ]
        )
        == 0
    )
    data = json.loads(report_out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.supply_chain_revalidation_report.v1"
    assert data["total_failures"] == 0

