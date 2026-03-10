"""M40 PR-2: runtime evidence to trace linkage contract checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import collect_runtime_evidence_v1 as collector  # noqa: E402


def _check(data: dict, check_id: str) -> dict:
    rows = [entry for entry in data["checks"] if entry["check_id"] == check_id]
    assert len(rows) == 1
    return rows[0]


def test_evidence_trace_linkage_v1_passes_for_runtime_artifacts(tmp_path: Path):
    out = tmp_path / "runtime-evidence-v1.json"
    assert collector.main(["--seed", "20260310", "--out", str(out)]) == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    trace_index = {trace["trace_id"]: trace for trace in data["traces"]}

    for item in data["evidence_items"]:
        trace_id = item["trace_id"]
        assert trace_id in trace_index
        linked_trace = trace_index[trace_id]
        assert item["trace_digest"] == linked_trace["trace_digest"]
        assert item["execution_lane"] == linked_trace["execution_lane"]

    assert _check(data, "trace_linkage_ratio")["pass"] is True
    assert _check(data, "detached_trace_count")["pass"] is True


def test_evidence_trace_linkage_v1_detects_detached_trace_failure(tmp_path: Path):
    out = tmp_path / "runtime-evidence-v1-detached.json"
    assert (
        collector.main(
            [
                "--inject-failure",
                "detached_trace_count",
                "--out",
                str(out),
            ]
        )
        == 1
    )

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["totals"]["detached_trace_count"] >= 1
    assert _check(data, "detached_trace_count")["pass"] is False
