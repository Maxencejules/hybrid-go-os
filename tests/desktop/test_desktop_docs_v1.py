"""M35 PR-1: desktop/display/input contract doc checks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_m35_pr1_desktop_contract_artifacts_exist():
    required = [
        "docs/M35_EXECUTION_BACKLOG.md",
        "docs/desktop/display_stack_contract_v1.md",
        "docs/desktop/window_manager_contract_v1.md",
        "docs/desktop/input_stack_contract_v1.md",
        "docs/desktop/desktop_profile_v1.md",
        "tests/desktop/test_desktop_docs_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M35 PR-1 artifact: {rel}"


def test_display_contract_v1_doc_declares_required_tokens():
    doc = _read("docs/desktop/display_stack_contract_v1.md")
    for token in [
        "Display stack contract ID: `rugo.display_stack_contract.v1`",
        "Parent desktop profile ID: `rugo.desktop_profile.v1`",
        "Smoke report schema: `rugo.desktop_smoke_report.v1`",
        "`display_mode_set`",
        "`display_scanout_stable`",
        "`session_handshake_ready`",
        "`session_desktop_ready`",
        "Local desktop gate: `make test-desktop-stack-v1`",
        "CI desktop gate: `Desktop stack v1 gate`",
    ]:
        assert token in doc


def test_window_manager_contract_v1_doc_declares_required_tokens():
    doc = _read("docs/desktop/window_manager_contract_v1.md")
    for token in [
        "Window manager contract ID: `rugo.window_manager_contract.v1`",
        "Parent desktop profile ID: `rugo.desktop_profile.v1`",
        "Smoke report schema: `rugo.desktop_smoke_report.v1`",
        "`window_create_ok`",
        "`window_map_ok`",
        "`window_focus_switch`",
        "`window_close_ok`",
        "window create latency: `<= 80 ms`",
        "window close latency: `<= 35 ms`",
    ]:
        assert token in doc


def test_input_stack_contract_v1_doc_declares_required_tokens():
    doc = _read("docs/desktop/input_stack_contract_v1.md")
    for token in [
        "Input stack contract ID: `rugo.input_stack_contract.v1`",
        "Parent desktop profile ID: `rugo.desktop_profile.v1`",
        "Input baseline report schema: `rugo.desktop_smoke_report.v1`",
        "`input_keyboard_latency`",
        "`input_pointer_latency`",
        "`input_focus_delivery`",
        "`input_repeat_consistency`",
        "keyboard event p95 latency must be `<= 12 ms`.",
        "input delivery success ratio must be `>= 0.995`",
    ]:
        assert token in doc


def test_desktop_profile_v1_doc_declares_required_tokens():
    doc = _read("docs/desktop/desktop_profile_v1.md")
    for token in [
        "Desktop profile ID: `rugo.desktop_profile.v1`",
        "Desktop smoke schema: `rugo.desktop_smoke_report.v1`",
        "GUI app matrix schema: `rugo.gui_app_matrix_report.v1`",
        "GUI app tier schema: `rugo.gui_app_tiers.v1`",
        "| `productivity` | `tier_productivity` | 6 | 0.83 |",
        "| `media` | `tier_media` | 4 | 0.75 |",
        "| `utility` | `tier_utility` | 5 | 0.80 |",
        "Local gate: `make test-desktop-stack-v1`",
        "Local sub-gate: `make test-gui-app-compat-v1`",
        "CI gate: `Desktop stack v1 gate`",
        "CI sub-gate: `GUI app compatibility v1 gate`",
    ]:
        assert token in doc


def test_m35_roadmap_anchor_declares_desktop_gates():
    roadmap = _read("docs/M35_M39_GENERAL_PURPOSE_EXPANSION_ROADMAP.md")
    assert "test-desktop-stack-v1" in roadmap
    assert "test-gui-app-compat-v1" in roadmap

