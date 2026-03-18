"""M31 PR-1: supply-chain revalidation and attestation doc contract checks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_m31_pr1_supply_chain_artifacts_exist():
    required = [
        "docs/M31_EXECUTION_BACKLOG.md",
        "docs/build/supply_chain_revalidation_policy_v1.md",
        "docs/build/release_attestation_policy_v1.md",
        "tools/verify_sbom_provenance_v2.py",
        "tools/verify_release_attestations_v1.py",
        "tests/build/test_supply_chain_revalidation_docs_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M31 PR-1 artifact: {rel}"


def test_supply_chain_revalidation_policy_v1_doc_declares_required_tokens():
    doc = _read("docs/build/supply_chain_revalidation_policy_v1.md")
    for token in [
        "Supply-chain policy ID: `rugo.supply_chain_revalidation_policy.v1`",
        "Revalidation report schema: `rugo.supply_chain_revalidation_report.v1`",
        "Attestation verification schema: `rugo.release_attestation_verification.v1`",
        "python tools/build_release_bundle_v1.py --out out/release-bundle-v1.json",
        "`out/release-bundle-v1.json`",
        "`sbom_exists`",
        "`sbom_schema`",
        "`provenance_exists`",
        "`provenance_schema`",
        "`subject_consistency`",
        "max_failures = 0",
        "max_drift = 0",
        "Local gate: `make test-supply-chain-revalidation-v1`",
        "CI gate: `Supply-chain revalidation v1 gate`",
        "Lifecycle integration: `make test-release-lifecycle-v2`",
    ]:
        assert token in doc


def test_release_attestation_policy_v1_doc_declares_required_tokens():
    doc = _read("docs/build/release_attestation_policy_v1.md")
    for token in [
        "Attestation policy ID: `release-attestation-v1`",
        "Verification schema: `rugo.release_attestation_verification.v1`",
        "`expected_policy_id`",
        "`observed_policy_id`",
        "`policy_match`",
        "`drift_count`",
        "`max_drift = 0`",
        "python tools/verify_release_attestations_v1.py --release-contract out/release-contract-v1.json --out out/release-attestation-verification-v1.json",
        "Any policy mismatch is gate-blocking.",
        "Any drift above threshold is gate-blocking.",
    ]:
        assert token in doc
