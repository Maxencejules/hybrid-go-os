"""M13 acceptance: storage recovery checker report."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out"

sys.path.append(str(ROOT / "tools"))
import storage_recover_v1 as recover  # noqa: E402


def _ensure_fs_image() -> Path:
    image = OUT / "fs-test.img"
    if image.is_file():
        return image

    mkfs = ROOT / "tools" / "mkfs.py"
    OUT.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [sys.executable, str(mkfs), str(image)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise AssertionError(
            "mkfs.py failed while preparing fs-test image:\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}"
        )
    return image


def test_storage_recovery_report_schema_and_mountability():
    image = _ensure_fs_image()
    data = recover.build_report(image_path=image, check_mode=True)
    assert data["schema"] == "rugo.storage_recovery_report.v1"
    assert data["image_present"] is True
    assert data["mountable"] is True
    assert data["total_issues"] == 0
    assert data["checks"]["magic_ok"] is True
