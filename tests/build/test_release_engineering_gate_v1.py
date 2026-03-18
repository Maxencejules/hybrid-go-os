"""M14 acceptance: release-engineering gate wiring and artifact schemas."""

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import build_release_bundle_v1 as bundle_tool  # noqa: E402
import collect_support_bundle_v1 as support_bundle  # noqa: E402
import generate_provenance_v1 as provenance  # noqa: E402
import generate_sbom_v1 as sbom  # noqa: E402
import release_contract_v1 as release_contract  # noqa: E402
import run_update_attack_suite_v1 as update_suite  # noqa: E402
import update_client_verify_v1 as verify_tool  # noqa: E402
import update_repo_sign_v1 as sign_tool  # noqa: E402


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_release_engineering_gate_wiring_and_artifacts(tmp_path: Path):
    required = [
        "docs/M14_EXECUTION_BACKLOG.md",
        "docs/build/default_lane_release_path_v1.md",
        "docs/build/release_policy_v1.md",
        "docs/build/versioning_scheme_v1.md",
        "docs/build/release_checklist_v1.md",
        "docs/build/supply_chain_policy_v1.md",
        "docs/build/installer_recovery_baseline_v1.md",
        "docs/pkg/update_protocol_v1.md",
        "docs/pkg/update_repo_layout_v1.md",
        "docs/security/update_signing_policy_v1.md",
        "tools/build_release_bundle_v1.py",
        "tools/release_contract_v1.py",
        "tools/update_repo_sign_v1.py",
        "tools/update_client_verify_v1.py",
        "tools/run_update_attack_suite_v1.py",
        "tools/generate_sbom_v1.py",
        "tools/generate_provenance_v1.py",
        "tools/collect_support_bundle_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M14 artifact: {rel}"

    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")
    milestones = _read("MILESTONES.md")
    status = _read("docs/STATUS.md")

    assert "test-release-engineering-v1" in makefile
    assert "tools/build_release_bundle_v1.py --channel stable --version 1.0.0 --build-sequence 1" in makefile
    assert "tools/release_contract_v1.py --channel stable --version 1.0.0 --build-sequence 1 --release-bundle $(OUT)/release-bundle-v1.json --out $(OUT)/release-contract-v1.json" in makefile
    assert "tools/update_repo_sign_v1.py --repo $(OUT)/update-repo-v1 --version 1.0.0 --build-sequence 1 --release-bundle $(OUT)/release-bundle-v1.json --out $(OUT)/update-metadata-v1.json" in makefile
    assert "Release engineering v1 gate" in ci
    assert "out/release-bundle-v1.json" in ci
    assert "M14" in milestones
    assert "M14" in status

    out_contract = tmp_path / "release-contract-v1.json"
    out_update = tmp_path / "update-metadata-v1.json"
    out_attack = tmp_path / "update-attack-suite-v1.json"
    out_sbom = tmp_path / "sbom-v1.spdx.json"
    out_prov = tmp_path / "provenance-v1.json"
    out_bundle = tmp_path / "support-bundle-v1.json"
    out_release_bundle = tmp_path / "release-bundle-v1.json"
    repo = tmp_path / "update-repo"
    state = tmp_path / "update-state.json"
    system_image = tmp_path / "os-go.iso"
    kernel = tmp_path / "kernel-go.elf"
    panic_image = tmp_path / "os-panic.iso"

    system_image.write_bytes(b"release-image\n")
    kernel.write_bytes(b"kernel-elf\n")
    panic_image.write_bytes(b"panic-image\n")

    assert (
        bundle_tool.main(
            [
                "--system-image",
                str(system_image),
                "--kernel",
                str(kernel),
                "--panic-image",
                str(panic_image),
                "--build-sequence",
                "22",
                "--capture-mode",
                "fixture",
                "--out",
                str(out_release_bundle),
            ]
        )
        == 0
    )

    assert (
        release_contract.main(
            [
                "--release-bundle",
                str(out_release_bundle),
                "--build-sequence",
                "22",
                "--out",
                str(out_contract),
            ]
        )
        == 0
    )
    assert (
        sign_tool.main(
            [
                "--repo",
                str(repo),
                "--out",
                str(out_update),
                "--version",
                "1.0.0",
                "--build-sequence",
                "22",
                "--release-bundle",
                str(out_release_bundle),
            ]
        )
        == 0
    )
    assert (
        verify_tool.main(
            [
                "--repo",
                str(repo),
                "--metadata",
                str(out_update),
                "--state",
                str(state),
                "--expect-version",
                "1.0.0",
            ]
        )
        == 0
    )
    assert (
        update_suite.main(
            [
                "--seed",
                "20260304",
                "--max-failures",
                "0",
                "--out",
                str(out_attack),
            ]
        )
        == 0
    )
    assert (
        sbom.main(
            [
                "--release-bundle",
                str(out_release_bundle),
                "--artifacts",
                str(out_contract),
                str(out_update),
                str(out_attack),
                "--out",
                str(out_sbom),
            ]
        )
        == 0
    )
    assert (
        provenance.main(
            [
                "--release-bundle",
                str(out_release_bundle),
                "--artifacts",
                str(out_contract),
                str(out_update),
                str(out_attack),
                "--out",
                str(out_prov),
            ]
        )
        == 0
    )
    assert (
        support_bundle.main(
            [
                "--release-bundle",
                str(out_release_bundle),
                "--artifacts",
                str(out_contract),
                str(out_attack),
                str(out_sbom),
                str(out_prov),
                "--out",
                str(out_bundle),
            ]
        )
        == 0
    )

    assert json.loads(out_release_bundle.read_text(encoding="utf-8"))["schema"] == (
        "rugo.release_bundle.v1"
    )
    assert json.loads(out_contract.read_text(encoding="utf-8"))["schema"] == (
        "rugo.release_contract.v1"
    )
    assert json.loads(out_attack.read_text(encoding="utf-8"))["schema"] == (
        "rugo.update_attack_suite_report.v1"
    )
    assert json.loads(out_sbom.read_text(encoding="utf-8"))["spdxVersion"] == "SPDX-2.3"
    assert json.loads(out_prov.read_text(encoding="utf-8"))["schema"] == "rugo.provenance.v1"
    assert json.loads(out_bundle.read_text(encoding="utf-8"))["schema"] == (
        "rugo.support_bundle.v1"
    )
