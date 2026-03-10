"""M45 PR-2: desktop display-device bridge checks."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_desktop_smoke_v1 as smoke  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _out_path(name: str) -> Path:
    path = ROOT / "out" / "pytest-m45" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    return path


def test_display_device_bridge_contract_tokens_present():
    doc = _read("docs/desktop/display_stack_contract_v1.md")
    for token in [
        "Display device bridge requirements",
        "`display_class`",
        "`display_device`",
        "`boot_transport_class`",
        "`desktop_display_checks`",
        "`virtio-gpu-pci`",
    ]:
        assert token in doc


def test_display_device_bridge_v1_schema_and_pass():
    out = _out_path("desktop-smoke-v1-bridge.json")
    rc = smoke.main(["--seed", "20260309", "--out", str(out)])
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.desktop_smoke_report.v1"
    assert data["display_class"] == "virtio-gpu-pci"
    assert data["boot_transport_class"] == "virtio-blk-pci-modern"
    assert data["display_device"]["driver"] == "virtio_gpu_framebuffer"
    assert data["display_device"]["desktop_qualified"] is True
    assert data["desktop_display_checks"]["bridge_pass"] is True
    assert data["desktop_display_checks"]["qualifying_checks"] == [
        "display_mode_set",
        "display_scanout_stable",
        "session_handshake_ready",
        "session_desktop_ready",
    ]


def test_display_device_bridge_v1_detects_display_failure():
    out = _out_path("desktop-smoke-v1-bridge-fail.json")
    rc = smoke.main(
        [
            "--inject-failure",
            "display_mode_set",
            "--out",
            str(out),
        ]
    )
    assert rc == 1

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["gate_pass"] is False
    assert data["desktop_display_checks"]["bridge_pass"] is False
    assert data["display_device"]["desktop_qualified"] is False
