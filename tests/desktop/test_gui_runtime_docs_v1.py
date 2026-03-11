"""M51 PR-1: GUI runtime contract doc checks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_m51_pr1_gui_runtime_artifacts_exist():
    required = [
        "docs/M51_EXECUTION_BACKLOG.md",
        "docs/desktop/gui_runtime_contract_v1.md",
        "docs/desktop/toolkit_profile_v1.md",
        "docs/desktop/font_text_rendering_policy_v1.md",
        "tests/desktop/test_gui_runtime_docs_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M51 PR-1 artifact: {rel}"


def test_gui_runtime_contract_v1_doc_declares_required_tokens():
    doc = _read("docs/desktop/gui_runtime_contract_v1.md")
    for token in [
        "GUI runtime contract ID: `rugo.gui_runtime_contract.v1`.",
        "Parent window system contract ID: `rugo.window_manager_contract.v2`.",
        "Parent seat contract ID: `rugo.seat_input_contract.v1`.",
        "Runtime report schema: `rugo.gui_runtime_report.v1`.",
        "Toolkit compatibility schema: `rugo.toolkit_compat_report.v1`.",
        "`app_launch_budget`",
        "`first_frame_budget`",
        "`input_roundtrip_budget`",
        "`text_glyph_cache_integrity`",
        "`event_loop_wakeup_budget`",
        "Local gate: `make test-gui-runtime-v1`.",
        "Local sub-gate: `make test-toolkit-compat-v1`.",
        "CI gate: `GUI runtime v1 gate`.",
        "CI sub-gate: `Toolkit compatibility v1 gate`.",
    ]:
        assert token in doc


def test_toolkit_profile_v1_doc_declares_required_tokens():
    doc = _read("docs/desktop/toolkit_profile_v1.md")
    for token in [
        "Toolkit profile ID: `rugo.toolkit_profile.v1`.",
        "Parent GUI runtime contract ID: `rugo.gui_runtime_contract.v1`.",
        "Runtime report schema: `rugo.gui_runtime_report.v1`.",
        "Toolkit compatibility schema: `rugo.toolkit_compat_report.v1`.",
        "Declared retained profile: `rugo.widgets.retain.v1`.",
        "Declared overlay profile: `rugo.canvas.overlay.v1`.",
        "`label`, `button`, `text_field`, `scroll_view`, `panel`",
        "`toast`, `icon`, `label`, `panel`",
        "minimum compatible cases: `3`",
        "minimum compatible cases: `1`",
    ]:
        assert token in doc


def test_font_text_rendering_policy_v1_doc_declares_required_tokens():
    doc = _read("docs/desktop/font_text_rendering_policy_v1.md")
    for token in [
        "Font/text rendering policy ID: `rugo.font_text_rendering_policy.v1`.",
        "Parent GUI runtime contract ID: `rugo.gui_runtime_contract.v1`.",
        "Runtime report schema: `rugo.gui_runtime_report.v1`.",
        "Toolkit compatibility schema: `rugo.toolkit_compat_report.v1`.",
        "Default font family: `rugo-sans`.",
        "Fallback font family: `rugo-mono`.",
        "Declared shaping profile: `ascii-plus-latin-1-no-complex-shaping`.",
        "`text_glyph_cache_integrity`",
        "`font_fallback_integrity`",
        "`baseline_grid_alignment`",
    ]:
        assert token in doc


def test_m51_roadmap_anchor_declares_gui_runtime_gates():
    roadmap = _read("docs/M48_M52_GUI_IMPLEMENTATION_ROADMAP.md")
    assert "test-gui-runtime-v1" in roadmap
    assert "test-toolkit-compat-v1" in roadmap
