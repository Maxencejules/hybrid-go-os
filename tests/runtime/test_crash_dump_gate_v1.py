"""M29 aggregate gate: crash dump capture + symbolization pipeline."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import collect_crash_dump_v1 as collector  # noqa: E402
import symbolize_crash_dump_v1 as symbolizer  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_crash_dump_gate_v1(tmp_path: Path):
    required = [
        "docs/runtime/crash_dump_contract_v1.md",
        "docs/runtime/postmortem_triage_playbook_v1.md",
        "tools/collect_crash_dump_v1.py",
        "tools/symbolize_crash_dump_v1.py",
        "tests/runtime/test_crash_dump_capture_v1.py",
        "tests/runtime/test_crash_dump_symbolization_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing gate artifact: {rel}"

    roadmap = _read("docs/M21_M34_MATURITY_PARITY_ROADMAP.md")
    assert "test-crash-dump-v1" in roadmap

    dump = tmp_path / "crash-dump-v1.json"
    sym = tmp_path / "crash-dump-symbolized-v1.json"
    assert collector.main(["--out", str(dump)]) == 0
    assert symbolizer.main(["--dump", str(dump), "--out", str(sym)]) == 0
    data = json.loads(sym.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.crash_dump_symbolized.v1"
    assert len(data["frames"]) >= 1

