"""M36 PR-2: deterministic socket family expansion campaign checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_compat_surface_campaign_v1 as campaign  # noqa: E402
import run_posix_gap_report_v1 as gap  # noqa: E402


def _check(data: dict, check_id: str) -> dict:
    rows = [entry for entry in data["checks"] if entry["check_id"] == check_id]
    assert len(rows) == 1
    return rows[0]


def _required_row(data: dict, surface: str) -> dict:
    rows = [entry for entry in data["required_surfaces"] if entry["surface"] == surface]
    assert len(rows) == 1
    return rows[0]


def test_socket_family_expansion_v1_schema_and_pass(tmp_path: Path):
    out = tmp_path / "compat-surface-v1-socket.json"
    rc = campaign.main(["--seed", "20260309", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.compat_surface_campaign_report.v1"
    assert data["socket_contract_id"] == "rugo.socket_family_expansion.v1"
    assert data["summary"]["socket"]["pass"] is True
    assert data["socket"]["checks_pass"] is True
    assert data["socket"]["af_inet_stream_connect_ms"] <= 18
    assert data["socket"]["af_unix_stream_connect_ms"] <= 12
    assert _check(data, "socket_af_inet_stream")["pass"] is True
    assert _check(data, "socket_af_unix_dgram")["pass"] is True


def test_socket_family_expansion_v1_detects_unix_stream_failure(tmp_path: Path):
    out = tmp_path / "compat-surface-v1-socket-fail.json"
    rc = campaign.main(
        [
            "--inject-failure",
            "socket_af_unix_stream",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["summary"]["socket"]["failures"] >= 1
    assert _check(data, "socket_af_unix_stream")["pass"] is False


def test_socket_family_expansion_v1_aligns_with_posix_gap_required_rows(tmp_path: Path):
    out = tmp_path / "posix-gap-report-v1-socket.json"
    rc = gap.main(["--seed", "20260309", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert _required_row(data, "sendmsg")["status"] == "implemented"
    assert _required_row(data, "recvmsg")["status"] == "implemented"
    assert _required_row(data, "socketpair")["status"] == "implemented"
