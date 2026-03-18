"""End-to-end default-lane shipping path checks for T3."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "tools"))

import build_installer_v2 as installer_tool  # noqa: E402
import build_release_bundle_v1 as bundle_tool  # noqa: E402
import collect_support_bundle_v2 as support_bundle  # noqa: E402
import generate_provenance_v1 as provenance_tool  # noqa: E402
import generate_sbom_v1 as sbom_tool  # noqa: E402
import release_branch_audit_v2 as branch_audit  # noqa: E402
import release_contract_v1 as release_contract  # noqa: E402
import run_recovery_drill_v3 as recovery_v3  # noqa: E402
import run_upgrade_drill_v3 as upgrade_v3  # noqa: E402
import run_upgrade_recovery_drill_v2 as upgrade_recovery_v2  # noqa: E402
import support_window_audit_v1 as support_audit  # noqa: E402
import update_repo_sign_v1 as sign_tool  # noqa: E402
import verify_release_attestations_v1 as attest_tool  # noqa: E402
import verify_sbom_provenance_v2 as provenance_verify  # noqa: E402


def _write_artifact(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def test_default_lane_release_path_roundtrip(tmp_path: Path):
    system_image = tmp_path / "os-go.iso"
    kernel = tmp_path / "kernel-go.elf"
    panic_image = tmp_path / "os-panic.iso"
    _write_artifact(system_image, b"bootable-default-image\n")
    _write_artifact(kernel, b"default-kernel-elf\n")
    _write_artifact(panic_image, b"panic-image\n")

    bundle_out = tmp_path / "release-bundle-v1.json"
    release_contract_out = tmp_path / "release-contract-v1.json"
    update_repo = tmp_path / "update-repo"
    update_metadata_out = tmp_path / "update-metadata-v1.json"
    installer_out = tmp_path / "installer-v2.json"
    install_state_out = tmp_path / "install-state-v1.json"
    upgrade_recovery_out = tmp_path / "upgrade-recovery-v2.json"
    upgrade_v3_out = tmp_path / "upgrade-drill-v3.json"
    recovery_v3_out = tmp_path / "recovery-drill-v3.json"
    sbom_out = tmp_path / "sbom-v1.spdx.json"
    provenance_out = tmp_path / "provenance-v1.json"
    supply_chain_out = tmp_path / "supply-chain-revalidation-v1.json"
    attestation_out = tmp_path / "release-attestation-verification-v1.json"
    support_bundle_out = tmp_path / "support-bundle-v2.json"
    branch_out = tmp_path / "release-branch-audit-v2.json"
    support_out = tmp_path / "support-window-audit-v1.json"

    assert (
        bundle_tool.main(
            [
                "--channel",
                "stable",
                "--version",
                "1.0.0",
                "--build-sequence",
                "15",
                "--system-image",
                str(system_image),
                "--kernel",
                str(kernel),
                "--panic-image",
                str(panic_image),
                "--capture-mode",
                "fixture",
                "--out",
                str(bundle_out),
            ]
        )
        == 0
    )
    assert (
        release_contract.main(
            [
                "--channel",
                "stable",
                "--version",
                "1.0.0",
                "--build-sequence",
                "15",
                "--release-bundle",
                str(bundle_out),
                "--out",
                str(release_contract_out),
            ]
        )
        == 0
    )
    assert (
        sign_tool.main(
            [
                "--repo",
                str(update_repo),
                "--version",
                "1.0.0",
                "--build-sequence",
                "15",
                "--release-bundle",
                str(bundle_out),
                "--out",
                str(update_metadata_out),
            ]
        )
        == 0
    )
    assert (
        installer_tool.main(
            [
                "--channel",
                "stable",
                "--version",
                "1.0.0",
                "--build-sequence",
                "15",
                "--release-bundle",
                str(bundle_out),
                "--install-state-out",
                str(install_state_out),
                "--out",
                str(installer_out),
            ]
        )
        == 0
    )
    assert (
        upgrade_recovery_v2.main(
            [
                "--seed",
                "20260309",
                "--release-bundle",
                str(bundle_out),
                "--install-state",
                str(install_state_out),
                "--update-metadata",
                str(update_metadata_out),
                "--out",
                str(upgrade_recovery_out),
            ]
        )
        == 0
    )
    assert (
        upgrade_v3.main(
            [
                "--seed",
                "20260309",
                "--release-bundle",
                str(bundle_out),
                "--install-state",
                str(install_state_out),
                "--update-metadata",
                str(update_metadata_out),
                "--out",
                str(upgrade_v3_out),
            ]
        )
        == 0
    )
    assert (
        recovery_v3.main(
            [
                "--seed",
                "20260309",
                "--release-bundle",
                str(bundle_out),
                "--install-state",
                str(install_state_out),
                "--out",
                str(recovery_v3_out),
            ]
        )
        == 0
    )
    assert (
        sbom_tool.main(
            [
                "--version",
                "1.0.0",
                "--release-bundle",
                str(bundle_out),
                "--artifacts",
                str(release_contract_out),
                str(update_metadata_out),
                "--out",
                str(sbom_out),
            ]
        )
        == 0
    )
    assert (
        provenance_tool.main(
            [
                "--version",
                "1.0.0",
                "--release-bundle",
                str(bundle_out),
                "--artifacts",
                str(release_contract_out),
                str(update_metadata_out),
                "--out",
                str(provenance_out),
            ]
        )
        == 0
    )
    assert (
        provenance_verify.main(
            [
                "--sbom",
                str(sbom_out),
                "--provenance",
                str(provenance_out),
                "--release-bundle",
                str(bundle_out),
                "--out",
                str(supply_chain_out),
            ]
        )
        == 0
    )
    assert (
        attest_tool.main(
            [
                "--release-contract",
                str(release_contract_out),
                "--observed-policy-id",
                "release-attestation-v1",
                "--observed-drift",
                "0",
                "--max-drift",
                "0",
                "--out",
                str(attestation_out),
            ]
        )
        == 0
    )
    assert (
        support_bundle.main(
            [
                "--artifacts",
                str(installer_out),
                str(upgrade_recovery_out),
                "--release-bundle",
                str(bundle_out),
                "--install-state",
                str(install_state_out),
                "--out",
                str(support_bundle_out),
            ]
        )
        == 0
    )
    assert (
        branch_audit.main(
            [
                "--release-bundle",
                str(bundle_out),
                "--out",
                str(branch_out),
            ]
        )
        == 0
    )
    assert (
        support_audit.main(
            [
                "--release-bundle",
                str(bundle_out),
                "--out",
                str(support_out),
            ]
        )
        == 0
    )

    bundle_data = json.loads(bundle_out.read_text(encoding="utf-8"))
    assert bundle_data["schema"] == "rugo.release_bundle.v1"
    assert bundle_data["runtime_capture"]["capture_mode"] == "fixture"
    bootable_roles = {
        artifact["role"]
        for artifact in bundle_data["artifacts"]
        if artifact["bootable"] is True
    }
    assert {"system_image", "installer_image", "recovery_image", "panic_image"} <= bootable_roles

    contract_data = json.loads(release_contract_out.read_text(encoding="utf-8"))
    assert contract_data["default_lane_release"]["release_bundle_digest"] == bundle_data["digest"]
    assert contract_data["attestation_policy_id"] == "release-attestation-v1"

    metadata_data = json.loads(update_metadata_out.read_text(encoding="utf-8"))
    target_names = {target["path"] for target in metadata_data["targets"]}
    assert any(name.endswith("system.iso") for name in target_names)
    assert any(name.endswith("installer.iso") for name in target_names)
    assert any(name.endswith("recovery.iso") for name in target_names)

    install_state = json.loads(install_state_out.read_text(encoding="utf-8"))
    assert install_state["schema"] == "rugo.install_state.v1"
    assert install_state["release_bundle_digest"] == bundle_data["digest"]

    upgrade_data = json.loads(upgrade_v3_out.read_text(encoding="utf-8"))
    assert upgrade_data["release_bundle_digest"] == bundle_data["digest"]
    assert upgrade_data["state_transition"]["active_slot_after"] == "B"

    recovery_data = json.loads(recovery_v3_out.read_text(encoding="utf-8"))
    assert recovery_data["release_bundle_digest"] == bundle_data["digest"]
    assert recovery_data["recovery_readiness"]["state_capture_complete"] is True

    supply_chain = json.loads(supply_chain_out.read_text(encoding="utf-8"))
    checks = {entry["name"]: entry["pass"] for entry in supply_chain["checks"]}
    assert checks["bundle_subject_coverage"] is True
    assert checks["bundle_sbom_coverage"] is True

    attestation = json.loads(attestation_out.read_text(encoding="utf-8"))
    assert attestation["release_bundle_attached"] is True
    assert attestation["meets_target"] is True

    support_data = json.loads(support_bundle_out.read_text(encoding="utf-8"))
    assert support_data["release_context"]["release_bundle_digest"] == bundle_data["digest"]
    assert support_data["release_context"]["active_slot"] == "A"

    branch_data = json.loads(branch_out.read_text(encoding="utf-8"))
    assert branch_data["release_reference"]["release_bundle_digest"] == bundle_data["digest"]
    support_window = json.loads(support_out.read_text(encoding="utf-8"))
    assert support_window["release_reference"]["release_bundle_digest"] == bundle_data["digest"]
