"""M14 acceptance: update rollback/replay protection semantics."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import update_client_verify_v1 as verify_tool  # noqa: E402
import update_repo_sign_v1 as sign_tool  # noqa: E402


def test_update_replay_and_rollback_rejected(tmp_path: Path):
    repo = tmp_path / "repo"
    state = tmp_path / "client-state-v1.json"

    seq10 = tmp_path / "seq10.json"
    rc_sign_10 = sign_tool.main(
        [
            "--repo",
            str(repo),
            "--version",
            "1.0.0",
            "--build-sequence",
            "10",
            "--out",
            str(seq10),
        ]
    )
    assert rc_sign_10 == 0

    rc_ok = verify_tool.main(
        [
            "--repo",
            str(repo),
            "--metadata",
            str(seq10),
            "--state",
            str(state),
            "--expect-version",
            "1.0.0",
        ]
    )
    assert rc_ok == 0

    rc_replay = verify_tool.main(
        [
            "--repo",
            str(repo),
            "--metadata",
            str(seq10),
            "--state",
            str(state),
            "--expect-version",
            "1.0.0",
        ]
    )
    assert rc_replay == 1

    seq9 = tmp_path / "seq9.json"
    rc_sign_9 = sign_tool.main(
        [
            "--repo",
            str(repo),
            "--version",
            "1.0.0",
            "--build-sequence",
            "9",
            "--out",
            str(seq9),
        ]
    )
    assert rc_sign_9 == 0

    rc_rollback = verify_tool.main(
        [
            "--repo",
            str(repo),
            "--metadata",
            str(seq9),
            "--state",
            str(state),
            "--expect-version",
            "1.0.0",
        ]
    )
    assert rc_rollback == 1
