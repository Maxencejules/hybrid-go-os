"""M14 acceptance: update metadata sign + verify happy path."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import update_client_verify_v1 as verify_tool  # noqa: E402
import update_repo_sign_v1 as sign_tool  # noqa: E402


def test_update_metadata_sign_and_verify_roundtrip(tmp_path: Path):
    repo = tmp_path / "repo"
    metadata = tmp_path / "update-metadata-v1.json"
    state = tmp_path / "client-state-v1.json"

    rc_sign = sign_tool.main(
        [
            "--repo",
            str(repo),
            "--version",
            "1.0.0",
            "--build-sequence",
            "12",
            "--out",
            str(metadata),
        ]
    )
    assert rc_sign == 0
    assert metadata.is_file()

    data = json.loads(metadata.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.update_metadata.v1"
    assert data["build_sequence"] == 12
    assert data["channel"] == "stable"
    assert len(data["targets"]) >= 1
    assert data["signature"]["alg"] == "hmac-sha256"

    rc_verify = verify_tool.main(
        [
            "--repo",
            str(repo),
            "--metadata",
            str(metadata),
            "--state",
            str(state),
            "--expect-version",
            "1.0.0",
        ]
    )
    assert rc_verify == 0
    assert state.is_file()
