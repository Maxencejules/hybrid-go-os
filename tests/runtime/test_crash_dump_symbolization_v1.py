"""M29 acceptance: crash dump symbolization output schema."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import collect_crash_dump_v1 as collector  # noqa: E402
import symbolize_crash_dump_v1 as symbolizer  # noqa: E402


def test_crash_dump_symbolization_v1(tmp_path: Path):
    dump = tmp_path / "crash-dump-v1.json"
    sym = tmp_path / "crash-dump-symbolized-v1.json"
    assert collector.main(["--out", str(dump)]) == 0
    assert symbolizer.main(["--dump", str(dump), "--out", str(sym)]) == 0
    data = json.loads(sym.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.crash_dump_symbolized.v1"
    assert data["source_schema"] == "rugo.crash_dump.v1"
    assert len(data["frames"]) >= 1
    assert "symbol" in data["frames"][0]

