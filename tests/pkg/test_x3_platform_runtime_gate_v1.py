"""X3 aggregate gate: platform/ecosystem runtime-backed closure wiring and docs."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import run_x3_platform_runtime_v1 as tool  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _work_dir(name: str) -> Path:
    path = ROOT / "out" / "pytest-x3" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_x3_platform_runtime_gate_v1_wiring_and_artifacts():
    required = [
        "docs/pkg/x3_platform_ecosystem_runtime_qualification_v1.md",
        "tools/x3_platform_runtime_common_v1.py",
        "tools/run_x3_platform_runtime_v1.py",
        "tests/pkg/test_x3_platform_runtime_v1.py",
        "tests/pkg/test_x3_platform_runtime_service_v1.py",
        "tests/pkg/test_x3_platform_runtime_gate_v1.py",
        "docs/roadmap/implementation_closure/expansion_breadth.md",
        "docs/M26_EXECUTION_BACKLOG.md",
        "docs/M38_EXECUTION_BACKLOG.md",
        "docs/M39_EXECUTION_BACKLOG.md",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing X3 artifact: {rel}"

    roadmap = _read("docs/roadmap/implementation_closure/expansion_breadth.md")
    summary = _read("docs/roadmap/README.md")
    framework = _read("docs/roadmap/MILESTONE_FRAMEWORK.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    readme = _read("README.md")

    assert "The historical X3 platform and ecosystem backlog is now runtime-backed" in roadmap
    for row in [
        "| `M26 Package/Repo Ecosystem v3` | `Runtime-backed` |",
        "| `M38 Storage + Platform Feature Expansion v1` | `Runtime-backed` |",
        "| `M39 Ecosystem Scale + Distribution Workflow v1` | `Runtime-backed` |",
    ]:
        assert row in roadmap

    assert "historical X3 platform and ecosystem backlog is closed on a shared runtime-backed qualification lane" in summary
    assert "historical X3 platform and ecosystem backlog is closed on a shared runtime-backed qualification lane" in framework
    assert "make test-x3-platform-runtime-v1" in readme

    assert "test-x3-platform-runtime-v1" in makefile
    for entry in [
        "tools/run_x3_platform_runtime_v1.py --runtime-capture $(OUT)/booted-runtime-v1.json --emit-supporting-reports --supporting-dir $(OUT) --out $(OUT)/x3-platform-runtime-v1.json",
        "tests/pkg/test_x3_platform_runtime_v1.py",
        "tests/pkg/test_x3_platform_runtime_gate_v1.py",
        "tests/pkg/test_x3_platform_runtime_service_v1.py",
    ]:
        assert entry in makefile
    assert "pytest-x3-platform-runtime-v1.xml" in makefile

    assert "X3 platform runtime v1 gate" in ci
    assert "make test-x3-platform-runtime-v1" in ci
    assert "x3-platform-runtime-v1-artifacts" in ci
    assert "out/pytest-x3-platform-runtime-v1.xml" in ci
    assert "out/x3-platform-runtime-v1.json" in ci

    for relpath in [
        "docs/M26_EXECUTION_BACKLOG.md",
        "docs/M38_EXECUTION_BACKLOG.md",
        "docs/M39_EXECUTION_BACKLOG.md",
    ]:
        doc = _read(relpath)
        assert "X3 runtime-backed closure addendum (2026-03-18)" in doc
        assert "x3 platform and ecosystem runtime qualification" in doc.lower()

    work_dir = _work_dir("gate")
    out = work_dir / "x3-platform-runtime-v1.json"
    support_dir = work_dir / "supporting"
    rc = tool.main(
        [
            "--seed",
            "20260318",
            "--fixture",
            "--emit-supporting-reports",
            "--supporting-dir",
            str(support_dir),
            "--out",
            str(out),
        ]
    )
    assert rc == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "rugo.x3_platform_ecosystem_runtime_report.v1"
    assert data["gate_pass"] is True

    for name in [
        "repo-policy-v3.json",
        "pkg-rebuild-v3.json",
        "update-trust-v1.json",
        "storage-feature-v1.json",
        "platform-feature-v1.json",
        "app-catalog-sim-v1.json",
        "pkg-install-success-v1.json",
        "catalog-audit-v1.json",
    ]:
        assert (support_dir / name).is_file(), f"missing emitted supporting report: {name}"
