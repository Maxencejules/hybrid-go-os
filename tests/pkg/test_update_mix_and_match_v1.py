"""M26 acceptance: mix-and-match metadata attack remains blocked."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import check_update_trust_v1 as trust  # noqa: E402


def test_update_mix_and_match_attack_blocked(tmp_path: Path):
    out = tmp_path / "update-trust-v1.json"
    rc = trust.main(["--out", str(out), "--max-failures", "0"])
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    case = next(c for c in data["cases"] if c["name"] == "mix_and_match_attack")
    assert case["blocked"] is True
    assert case["pass"] is True

