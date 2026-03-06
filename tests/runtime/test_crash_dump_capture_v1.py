"""M29 acceptance: crash dump capture artifact schema."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import collect_crash_dump_v1 as collector  # noqa: E402


def test_crash_dump_capture_v1(tmp_path: Path):
    out = tmp_path / "crash-dump-v1.json"
    rc = collector.main(["--panic-code", "77", "--out", str(out)])
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.crash_dump.v1"
    assert data["panic_code"] == 77
    assert "registers" in data
    assert len(data["stack_frames"]) >= 1

