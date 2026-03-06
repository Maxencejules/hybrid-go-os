"""M31 acceptance: supply-chain revalidation docs and tooling presence."""

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (_repo_root() / relpath).read_text(encoding="utf-8").lower()


def test_supply_chain_revalidation_docs_v1_present():
    root = _repo_root()
    required = [
        "docs/build/supply_chain_revalidation_policy_v1.md",
        "docs/build/release_attestation_policy_v1.md",
        "tools/verify_sbom_provenance_v2.py",
        "tools/verify_release_attestations_v1.py",
    ]
    for rel in required:
        assert (root / rel).is_file(), f"missing M31 artifact: {rel}"

    reval = _read("docs/build/supply_chain_revalidation_policy_v1.md")
    attest = _read("docs/build/release_attestation_policy_v1.md")
    assert "sbom" in reval
    assert "provenance" in reval
    assert "drift" in reval
    assert "attestation" in attest
    assert "policy" in attest

