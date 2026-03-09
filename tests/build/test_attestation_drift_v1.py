"""M31 acceptance: release attestation drift check."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import verify_release_attestations_v1 as attest  # noqa: E402


def test_attestation_drift_v1(tmp_path: Path):
    out = tmp_path / "release-attestation-verification-v1.json"
    rc = attest.main(
        [
            "--expected-policy-id",
            "release-attestation-v1",
            "--observed-policy-id",
            "release-attestation-v1",
            "--observed-drift",
            "0",
            "--max-drift",
            "0",
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.release_attestation_verification.v1"
    assert data["policy_match"] is True
    assert data["drift_count"] == 0


def test_attestation_drift_v1_blocks_policy_mismatch(tmp_path: Path):
    out = tmp_path / "release-attestation-verification-v1.json"
    rc = attest.main(
        [
            "--expected-policy-id",
            "release-attestation-v1",
            "--observed-policy-id",
            "release-attestation-v0",
            "--observed-drift",
            "1",
            "--max-drift",
            "0",
            "--out",
            str(out),
        ]
    )
    assert rc == 1
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.release_attestation_verification.v1"
    assert data["policy_match"] is False
    assert data["drift_count"] == 1
    assert data["meets_target"] is False
