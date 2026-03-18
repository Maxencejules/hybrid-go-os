# Default Lane Release Path v1

Date: 2026-03-18  
Track: T3 Release and Recovery Infrastructure  
Status: active default-lane shipping flow

## Purpose

Define the real shipping path for the current default `image-go` lane so
release, install, upgrade, recovery, provenance, and support workflows all
operate on the same staged bootable artifacts.

## Shared bundle contract

- Bundle schema: `rugo.release_bundle.v1`
- Install state schema: `rugo.install_state.v1`
- Bundle builder:
  - `python tools/build_release_bundle_v1.py --out out/release-bundle-v1.json`
- Default staged directory:
  - `out/releases/<channel>/<version>+build.<sequence>/`

## Staged bootable media

Each bundle stages versioned copies of the current default-lane bootable image:

- system image
- installer image
- recovery image
- panic validation image
- paired kernel ELF
- generated release notes and runtime capture

Installer and recovery media currently reuse the shipped default lane ISO.
That keeps the supported product scope honest: the repo now ships real,
versioned media for those roles, but support claims still only cover the
default QEMU lane.

## End-to-end flow

1. Build the bootable default lane image:
   - `make image-demo image-panic`
2. Stage the shipping bundle:
   - `python tools/build_release_bundle_v1.py --system-image out/os-go.iso --kernel out/kernel-go.elf --panic-image out/os-panic.iso --out out/release-bundle-v1.json`
3. Publish signed update metadata for the staged media:
   - `python tools/update_repo_sign_v1.py --release-bundle out/release-bundle-v1.json --out out/update-metadata-v1.json`
4. Materialize installer state:
   - `python tools/build_installer_v2.py --release-bundle out/release-bundle-v1.json --install-state-out out/install-state-v1.json --out out/installer-v2.json`
5. Run upgrade and recovery drills on the staged media:
   - `python tools/run_upgrade_recovery_drill_v2.py --release-bundle out/release-bundle-v1.json --install-state out/install-state-v1.json --update-metadata out/update-metadata-v1.json --out out/upgrade-recovery-v2.json`
   - `python tools/run_upgrade_drill_v3.py --release-bundle out/release-bundle-v1.json --install-state out/install-state-v1.json --update-metadata out/update-metadata-v1.json --out out/upgrade-drill-v3.json`
   - `python tools/run_recovery_drill_v3.py --release-bundle out/release-bundle-v1.json --install-state out/install-state-v1.json --out out/recovery-drill-v3.json`
6. Revalidate provenance and collect support evidence:
   - `python tools/generate_sbom_v1.py --release-bundle out/release-bundle-v1.json --out out/sbom-v1.spdx.json`
   - `python tools/generate_provenance_v1.py --release-bundle out/release-bundle-v1.json --out out/provenance-v1.json`
   - `python tools/verify_sbom_provenance_v2.py --release-bundle out/release-bundle-v1.json --out out/supply-chain-revalidation-v1.json`
   - `python tools/collect_support_bundle_v2.py --release-bundle out/release-bundle-v1.json --install-state out/install-state-v1.json --out out/support-bundle-v2.json`

## Required gate hooks

- `make test-release-engineering-v1`
- `make test-release-ops-v2`
- `make test-ops-ux-v3`
- `make test-release-lifecycle-v2`
