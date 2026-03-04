"""M12 acceptance: network trace capture helper output schema."""

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2] / "tools"))
import net_trace_capture_v1 as trace_tool  # noqa: E402


def test_trace_capture_report_schema(tmp_path: Path):
    serial_log = tmp_path / "serial.log"
    serial_log.write_text(
        "NET: virtio-net ready\nNET: udp echo\nRUGO: halt ok\n",
        encoding="utf-8",
    )
    out = tmp_path / "trace.json"
    rc = trace_tool.main(["--serial-log", str(serial_log), "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.net_trace_capture.v1"
    assert "NET: virtio-net ready" in data["markers_found"]
    assert "NET: udp echo" in data["markers_found"]
