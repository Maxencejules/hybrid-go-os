"""Roadmap docs: C3 completion status stays aligned with live runtime evidence."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_milestone_framework_marks_c3_done_and_c4_in_progress():
    doc = _read("docs/roadmap/MILESTONE_FRAMEWORK.md")
    assert "| `C3` Contracted Service OS Runtime | done |" in doc
    assert "| `C4` Durable and Connected Runtime | in progress |" in doc
    assert "`C3` done; `C4` in progress;" in doc


def test_roadmap_summary_current_phase_reflects_c3_completion():
    doc = _read("docs/roadmap/README.md")
    assert "`C3` done; `C4` in progress;" in doc
