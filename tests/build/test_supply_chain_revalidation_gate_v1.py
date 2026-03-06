"""M31 aggregate gate: supply-chain revalidation and attestation checks."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import generate_provenance_v1 as provenance  # noqa: E402
import generate_sbom_v1 as sbom  # noqa: E402
import verify_release_attestations_v1 as attest  # noqa: E402
import verify_sbom_provenance_v2 as verify  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_supply_chain_revalidation_gate_v1(tmp_path: Path):
    required = [
        "docs/build/supply_chain_revalidation_policy_v1.md",
        "docs/build/release_attestation_policy_v1.md",
        "tools/verify_sbom_provenance_v2.py",
        "tools/verify_release_attestations_v1.py",
        "tests/build/test_sbom_revalidation_v1.py",
        "tests/build/test_provenance_verification_v1.py",
        "tests/build/test_attestation_drift_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing gate artifact: {rel}"

    roadmap = _read("docs/M21_M34_MATURITY_PARITY_ROADMAP.md")
    assert "test-supply-chain-revalidation-v1" in roadmap

    sbom_out = tmp_path / "sbom-v1.spdx.json"
    prov_out = tmp_path / "provenance-v1.json"
    reval_out = tmp_path / "supply-chain-revalidation-v1.json"
    attest_out = tmp_path / "release-attestation-verification-v1.json"

    assert sbom.main(["--out", str(sbom_out)]) == 0
    assert provenance.main(["--out", str(prov_out)]) == 0
    assert verify.main(["--sbom", str(sbom_out), "--provenance", str(prov_out), "--out", str(reval_out)]) == 0
    assert attest.main(["--out", str(attest_out)]) == 0

    reval_data = json.loads(reval_out.read_text(encoding="utf-8"))
    attest_data = json.loads(attest_out.read_text(encoding="utf-8"))
    assert reval_data["total_failures"] == 0
    assert attest_data["meets_target"] is True

