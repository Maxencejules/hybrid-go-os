#!/usr/bin/env python3
"""M10 syscall-policy fuzz harness (model-level) with JSON report output."""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


RIGHT_READ = 1
RIGHT_WRITE = 2
RIGHT_POLL = 4
RIGHT_MASK = RIGHT_READ | RIGHT_WRITE | RIGHT_POLL


@dataclass
class FdState:
    kind: str
    rights: int


def _max_rights(kind: str) -> int:
    if kind == "console":
        return RIGHT_WRITE | RIGHT_POLL
    if kind == "file":
        return RIGHT_READ | RIGHT_POLL
    return 0


def _run_case(seed: int, iterations: int) -> Dict[str, int | str]:
    rng = random.Random(seed)
    # fd0/1/2 deterministic console descriptors
    fds: Dict[int, FdState] = {
        0: FdState("console", _max_rights("console")),
        1: FdState("console", _max_rights("console")),
        2: FdState("console", _max_rights("console")),
    }
    next_fd = 3
    violations = 0

    for _ in range(iterations):
        op = rng.randrange(0, 7)
        if op == 0:
            # open file
            mode = rng.choice([RIGHT_READ, RIGHT_WRITE, RIGHT_READ | RIGHT_WRITE])
            maxr = _max_rights("file")
            req = mode | RIGHT_POLL
            if req & ~maxr == 0:
                fds[next_fd] = FdState("file", req)
                next_fd += 1
        elif op == 1:
            # open console
            mode = rng.choice([RIGHT_READ, RIGHT_WRITE, RIGHT_READ | RIGHT_WRITE])
            maxr = _max_rights("console")
            req = mode | RIGHT_POLL
            if req & ~maxr == 0:
                fds[next_fd] = FdState("console", req)
                next_fd += 1
        elif op == 2 and fds:
            # reduce rights
            fd = rng.choice(list(fds.keys()))
            if fd < 3:
                continue
            req = rng.randrange(0, RIGHT_MASK + 1)
            if req & ~fds[fd].rights == 0:
                fds[fd].rights = req
        elif op == 3 and fds:
            # transfer rights
            fd = rng.choice(list(fds.keys()))
            if fd < 3:
                continue
            req = rng.randrange(1, RIGHT_MASK + 1)
            if req & ~fds[fd].rights == 0:
                fds[next_fd] = FdState(fds[fd].kind, req)
                next_fd += 1
                del fds[fd]
        elif op == 4 and fds:
            # close
            fd = rng.choice(list(fds.keys()))
            if fd >= 3:
                del fds[fd]
        else:
            # noop operations: read/write checks
            if not fds:
                continue
            fd = rng.choice(list(fds.keys()))
            st = fds[fd]
            if st.kind == "file" and (st.rights & RIGHT_READ) == 0:
                pass
            if st.kind == "console" and (st.rights & RIGHT_WRITE) == 0:
                pass

        # invariants: no handle exceeds kind max-rights
        for st in fds.values():
            if st.rights & ~_max_rights(st.kind):
                violations += 1

    return {
        "seed": seed,
        "iterations": iterations,
        "violations": violations,
        "open_fds": len(fds),
    }


def run_harness(seed: int, iterations: int, cases: int) -> Dict[str, object]:
    results: List[Dict[str, int | str]] = []
    total_violations = 0
    for i in range(cases):
        case_seed = seed + i
        case = _run_case(case_seed, iterations)
        results.append(case)
        total_violations += int(case["violations"])

    return {
        "schema": "rugo.security_fuzz_report.v1",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed_start": seed,
        "cases": cases,
        "iterations_per_case": iterations,
        "total_violations": total_violations,
        "crash_sla_hours": 24,
        "results": results,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed", type=int, default=1337)
    p.add_argument("--iterations", type=int, default=2000)
    p.add_argument("--cases", type=int, default=4)
    p.add_argument("--out", default="out/security-fuzz-report.json")
    return p


def main(argv: List[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    report = run_harness(
        seed=args.seed,
        iterations=args.iterations,
        cases=args.cases,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"fuzz-report: {out_path}")
    print(f"total_violations: {report['total_violations']}")
    return 0 if report["total_violations"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
