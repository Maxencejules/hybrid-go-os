#!/usr/bin/env python3
"""Run deterministic update attack simulations for M14."""

from __future__ import annotations

import argparse
import json
import random
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import update_client_verify_v1 as verify_tool
import update_repo_sign_v1 as sign_tool


def _read_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_suite(seed: int) -> Dict[str, object]:
    rng = random.Random(seed)
    key = "m14-update-key-v1"

    cases: List[Dict[str, object]] = []

    with tempfile.TemporaryDirectory(prefix="rugo-m14-update-") as tmp:
        root = Path(tmp)
        repo = root / "repo"
        state_path = root / "state.json"

        md_a = root / "metadata-seq10.json"
        sign_tool.main(
            [
                "--repo",
                str(repo),
                "--version",
                "1.0.0",
                "--build-sequence",
                "10",
                "--out",
                str(md_a),
                "--key",
                key,
                "--expires-hours",
                "168",
            ]
        )
        rc_baseline = verify_tool.main(
            [
                "--repo",
                str(repo),
                "--metadata",
                str(md_a),
                "--state",
                str(state_path),
                "--expect-version",
                "1.0.0",
                "--key",
                key,
            ]
        )
        cases.append(
            {
                "name": "baseline_accept",
                "kind": "control",
                "expected_success": True,
                "success": rc_baseline == 0,
            }
        )

        # Replay: same metadata and state should now be rejected.
        rc_replay = verify_tool.main(
            [
                "--repo",
                str(repo),
                "--metadata",
                str(md_a),
                "--state",
                str(state_path),
                "--expect-version",
                "1.0.0",
                "--key",
                key,
            ]
        )
        cases.append(
            {
                "name": "replay_attack",
                "kind": "attack",
                "expected_success": False,
                "success": rc_replay == 0,
            }
        )

        # Rollback: lower sequence should be rejected.
        md_b = root / "metadata-seq9.json"
        sign_tool.main(
            [
                "--repo",
                str(repo),
                "--version",
                "1.0.0",
                "--build-sequence",
                "9",
                "--out",
                str(md_b),
                "--key",
                key,
                "--expires-hours",
                "168",
            ]
        )
        rc_rollback = verify_tool.main(
            [
                "--repo",
                str(repo),
                "--metadata",
                str(md_b),
                "--state",
                str(state_path),
                "--expect-version",
                "1.0.0",
                "--key",
                key,
            ]
        )
        cases.append(
            {
                "name": "rollback_attack",
                "kind": "attack",
                "expected_success": False,
                "success": rc_rollback == 0,
            }
        )

        # Freeze: expired metadata should be rejected.
        md_c = root / "metadata-expired.json"
        sign_tool.main(
            [
                "--repo",
                str(repo),
                "--version",
                "1.0.1",
                "--build-sequence",
                "11",
                "--out",
                str(md_c),
                "--key",
                key,
                "--expires-hours",
                "-1",
            ]
        )
        rc_freeze = verify_tool.main(
            [
                "--repo",
                str(repo),
                "--metadata",
                str(md_c),
                "--state",
                str(state_path),
                "--expect-version",
                "1.0.1",
                "--key",
                key,
            ]
        )
        cases.append(
            {
                "name": "freeze_attack",
                "kind": "attack",
                "expected_success": False,
                "success": rc_freeze == 0,
            }
        )

        # Signature tamper: mutate metadata signature and verify rejection.
        md_d = root / "metadata-tamper.json"
        sign_tool.main(
            [
                "--repo",
                str(repo),
                "--version",
                "1.0.2",
                "--build-sequence",
                str(12 + rng.randrange(1, 3)),
                "--out",
                str(md_d),
                "--key",
                key,
                "--expires-hours",
                "168",
            ]
        )
        tampered = _read_json(md_d)
        sig = dict(tampered.get("signature", {}))
        value = str(sig.get("value", ""))
        sig["value"] = ("0" if not value.startswith("0") else "1") + value[1:]
        tampered["signature"] = sig
        _write_json(md_d, tampered)
        rc_tamper = verify_tool.main(
            [
                "--repo",
                str(repo),
                "--metadata",
                str(md_d),
                "--state",
                str(state_path),
                "--expect-version",
                str(tampered["version"]),
                "--key",
                key,
            ]
        )
        cases.append(
            {
                "name": "signature_tamper_attack",
                "kind": "attack",
                "expected_success": False,
                "success": rc_tamper == 0,
            }
        )

    passed_cases = sum(1 for c in cases if c["success"] == c["expected_success"])
    total_cases = len(cases)
    total_failures = total_cases - passed_cases

    return {
        "schema": "rugo.update_attack_suite_report.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed": seed,
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "failed_cases": total_failures,
        "total_failures": total_failures,
        "cases": cases,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed", type=int, default=20260304)
    p.add_argument("--max-failures", type=int, default=0)
    p.add_argument("--out", default="out/update-attack-suite-v1.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    report = run_suite(seed=args.seed)
    report["max_failures"] = args.max_failures
    report["meets_target"] = report["total_failures"] <= args.max_failures

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"update-attack-suite-report: {out_path}")
    print(f"total_failures: {report['total_failures']}")
    return 0 if report["meets_target"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
