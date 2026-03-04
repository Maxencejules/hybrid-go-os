"""M14 acceptance: release contract report artifact schema."""

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2] / "tools"))
import release_contract_v1 as release_contract  # noqa: E402


def test_release_contract_report_schema(tmp_path: Path):
    out = tmp_path / "release-contract-v1.json"
    rc = release_contract.main(
        [
            "--channel",
            "stable",
            "--version",
            "1.0.0",
            "--build-sequence",
            "7",
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    assert out.is_file()

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.release_contract.v1"
    assert data["selected_channel"] == "stable"
    assert data["version"] == "1.0.0"
    assert data["build_sequence"] == 7
    assert set(data["channels"].keys()) == {"nightly", "beta", "stable"}
    assert "out/release-contract-v1.json" in data["required_artifacts"]
