"""M17 PR-2: POSIX subset coverage checks for compatibility profile v2."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))

from v2_model import PosixSurfaceModel  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_profile_v2_declares_required_optional_unsupported_surfaces():
    doc = _read("docs/abi/compat_profile_v2.md")
    for token in [
        "## Profile classes",
        "## Required subset (`required`)",
        "## Optional subset (`optional`)",
        "## Explicit unsupported list (`unsupported`)",
        "epoll",
        "io_uring",
    ]:
        assert token in doc


def test_posix_surface_model_passes_with_full_required_set():
    model = PosixSurfaceModel()
    implemented = set(model.required_surfaces)
    implemented.update({"accept4", "clock_nanosleep"})
    report = model.evaluate(implemented)

    assert report["schema"] == "rugo.posix_surface_report.v2"
    assert report["pass"] is True
    assert report["missing_required"] == []
    assert "accept4" in report["optional_present"]
    assert "clock_nanosleep" in report["optional_present"]


def test_posix_surface_model_reports_missing_required_surface():
    model = PosixSurfaceModel()
    implemented = set(model.required_surfaces)
    implemented.remove("socket")

    report = model.evaluate(implemented)
    assert report["pass"] is False
    assert report["missing_required"] == ["socket"]


def test_runtime_syscall_coverage_matrix_v2_tracks_m17_rows():
    matrix = _read("docs/runtime/syscall_coverage_matrix_v2.md")
    for token in [
        "Milestone: M17 Compatibility Profile v2",
        "`sys_open`",
        "`sys_poll`",
        "`sys_fd_rights_reduce`",
        "compatibility gate | `test-compat-v2`",
        "`tests/compat/test_external_apps_tier_v2.py`",
    ]:
        assert token in matrix

