"""M17 PR-2: external app tier thresholds and signed artifact checks."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(Path(__file__).resolve().parent))
sys.path.append(str(ROOT / "tools"))

import pkg_bootstrap_v1 as pkgv1  # noqa: E402
from v2_model import ExternalAppSample, ExternalAppTierModel  # noqa: E402


def _baseline_samples() -> list[ExternalAppSample]:
    samples = []

    # tier_a threshold: min 12, min pass rate 0.90
    for idx in range(12):
        samples.append(
            ExternalAppSample(
                app_id=f"tier-a-{idx:02d}",
                tier="tier_a",
                passed=idx != 11,  # 11/12 pass -> 0.916...
                signed=True,
                deterministic=True,
            )
        )

    # tier_b threshold: min 8, min pass rate 0.75
    for idx in range(8):
        samples.append(
            ExternalAppSample(
                app_id=f"tier-b-{idx:02d}",
                tier="tier_b",
                passed=idx not in {6, 7},  # 6/8 pass -> 0.75
                signed=True,
                deterministic=True,
            )
        )

    return samples


def test_signed_repo_metadata_roundtrip_for_v2_profile():
    payload = pkgv1.build_debug_write_app("APP: external v2 lane\n")
    blob = pkgv1.build_pkg_v1(
        "external-hello-v2",
        "2.0.0",
        payload,
        abi_profile="compat_profile_v2",
    )
    manifest, _ = pkgv1.parse_pkg_v1(blob)
    assert manifest["abi_profile"] == "compat_profile_v2"

    metadata = pkgv1.build_repo_metadata_for_pkg(
        pkg_manifest=manifest,
        pkg_filename="external-hello-v2.pkgv1",
        pkg_blob=blob,
        generated_at="2026-03-06T00:00:00+00:00",
    )
    signed = pkgv1.sign_repo_metadata(metadata, "m17-tier-key", key_id="m17-tier")
    assert pkgv1.verify_repo_metadata(signed, "m17-tier-key") is True

    tampered = dict(signed)
    tampered["metadata"] = dict(signed["metadata"])
    tampered["metadata"]["packages"] = list(signed["metadata"]["packages"])
    tampered["metadata"]["packages"][0] = dict(signed["metadata"]["packages"][0])
    tampered["metadata"]["packages"][0]["pkg_size"] += 1
    assert pkgv1.verify_repo_metadata(tampered, "m17-tier-key") is False


def test_external_app_tier_model_passes_thresholds_deterministically():
    model = ExternalAppTierModel()
    first = model.evaluate(_baseline_samples())
    second = model.evaluate(_baseline_samples())

    assert first == second
    assert first["schema"] == "rugo.external_app_tier_report.v2"
    assert first["gate_pass"] is True
    assert first["tiers"]["tier_a"]["eligible"] == 12
    assert first["tiers"]["tier_b"]["eligible"] == 8
    assert first["tiers"]["tier_a"]["pass_rate"] >= 0.90
    assert first["tiers"]["tier_b"]["pass_rate"] >= 0.75
    assert first["issues"] == []


def test_external_app_tier_model_rejects_unsigned_or_nondeterministic_inputs():
    model = ExternalAppTierModel()
    samples = _baseline_samples()
    samples[0] = ExternalAppSample(
        app_id=samples[0].app_id,
        tier=samples[0].tier,
        passed=samples[0].passed,
        signed=False,
        deterministic=True,
        abi_profile=samples[0].abi_profile,
    )
    samples[12] = ExternalAppSample(
        app_id=samples[12].app_id,
        tier=samples[12].tier,
        passed=samples[12].passed,
        signed=True,
        deterministic=False,
        abi_profile=samples[12].abi_profile,
    )

    report = model.evaluate(samples)
    reasons = {item["reason"] for item in report["issues"]}

    assert report["gate_pass"] is False
    assert "unsigned_artifact" in reasons
    assert "non_deterministic_result" in reasons


def test_go_std_qemu_marker_for_tier_b(qemu_serial_go_std):
    out = qemu_serial_go_std.stdout
    assert "GOSTD: ok" in out, f"Missing standard-go marker. Got:\n{out}"
