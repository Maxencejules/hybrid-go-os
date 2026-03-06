"""Deterministic reference model for M17 compatibility profile v2 semantics."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


USER_LIMIT = 0x0000_8000_0000_0000
R_X86_64_RELATIVE = 8
SUPPORTED_INTERPRETERS = frozenset({"/lib/rugo-ld.so.1"})


@dataclass(frozen=True)
class SegmentV2:
    seg_type: str
    vaddr: int
    memsz: int
    filesz: int


@dataclass(frozen=True)
class RelocationV2:
    reloc_type: int
    offset: int


@dataclass(frozen=True)
class ElfImageV2:
    elf_type: str
    entry: int
    segments: tuple[SegmentV2, ...]
    interpreter: str | None = None
    relocations: tuple[RelocationV2, ...] = ()


class ElfLoaderV2Model:
    """Small deterministic loader model for static/dynamic v2 policy."""

    def validate(self, image: ElfImageV2) -> tuple[bool, str]:
        if image.elf_type not in {"ET_EXEC", "ET_DYN"}:
            return False, "E_UNSUP"
        if image.entry <= 0 or image.entry >= USER_LIMIT:
            return False, "E_RANGE"
        if not image.segments:
            return False, "E_INVAL"

        load_ranges = []
        has_dynamic_segment = False
        has_interp_segment = False
        for seg in image.segments:
            if seg.memsz < seg.filesz or seg.memsz <= 0:
                return False, "E_INVAL"
            if seg.vaddr >= USER_LIMIT:
                return False, "E_RANGE"
            end = seg.vaddr + seg.memsz
            if end > USER_LIMIT or end < seg.vaddr:
                return False, "E_RANGE"

            if seg.seg_type == "PT_LOAD":
                load_ranges.append((seg.vaddr, end))
            elif seg.seg_type == "PT_DYNAMIC":
                has_dynamic_segment = True
            elif seg.seg_type == "PT_INTERP":
                has_interp_segment = True
            else:
                return False, "E_UNSUP"

        if not load_ranges:
            return False, "E_INVAL"

        dynamic_mode = has_dynamic_segment or has_interp_segment or bool(image.relocations)
        if dynamic_mode:
            if image.elf_type != "ET_DYN":
                return False, "E_INVAL"
            if image.interpreter not in SUPPORTED_INTERPRETERS:
                return False, "E_UNSUP"
            if len(image.relocations) > 1024:
                return False, "E_RANGE"
            for reloc in image.relocations:
                if reloc.reloc_type != R_X86_64_RELATIVE:
                    return False, "E_UNSUP"
                if not any(start <= reloc.offset < end for start, end in load_ranges):
                    return False, "E_FAULT"
        else:
            if image.elf_type != "ET_EXEC":
                return False, "E_INVAL"

        return True, "OK"


class PosixSurfaceModel:
    required_surfaces = frozenset(
        {
            "execve",
            "waitpid",
            "open",
            "read",
            "write",
            "close",
            "poll",
            "clock_gettime",
            "nanosleep",
            "sigaction",
            "kill",
            "socket",
            "bind",
            "listen",
            "accept",
            "connect",
            "send",
            "recv",
            "sendto",
            "recvfrom",
            "shutdown",
        }
    )

    optional_surfaces = frozenset(
        {
            "fork",
            "accept4",
            "clock_nanosleep",
            "sigprocmask",
        }
    )

    unsupported_surfaces = frozenset(
        {
            "epoll",
            "io_uring",
            "fanotify",
            "inotify",
            "eventfd",
            "timerfd",
            "namespaces",
            "cgroups",
            "af_unix_full_parity",
            "af_netlink",
        }
    )

    def evaluate(self, implemented_surfaces: set[str]) -> dict:
        implemented = set(implemented_surfaces)
        missing_required = sorted(self.required_surfaces - implemented)
        unexpected = sorted(
            implemented
            - self.required_surfaces
            - self.optional_surfaces
            - self.unsupported_surfaces
        )
        optional_present = sorted(self.optional_surfaces & implemented)
        return {
            "schema": "rugo.posix_surface_report.v2",
            "pass": len(missing_required) == 0,
            "missing_required": missing_required,
            "optional_present": optional_present,
            "unexpected": unexpected,
        }


@dataclass(frozen=True)
class ExternalAppSample:
    app_id: str
    tier: str
    passed: bool
    signed: bool
    deterministic: bool
    abi_profile: str = "compat_profile_v2"


class ExternalAppTierModel:
    """Deterministic threshold gate for external compatibility tiers."""

    def __init__(self):
        self.thresholds = {
            "tier_a": {"min_samples": 12, "min_pass_rate": 0.90},
            "tier_b": {"min_samples": 8, "min_pass_rate": 0.75},
        }

    def evaluate(self, samples: list[ExternalAppSample]) -> dict:
        buckets = {
            tier: {"eligible": 0, "passed": 0}
            for tier in sorted(self.thresholds.keys())
        }
        issues = []

        for sample in samples:
            if sample.tier not in buckets:
                issues.append({"app_id": sample.app_id, "reason": "unknown_tier"})
                continue
            if not sample.signed:
                issues.append({"app_id": sample.app_id, "reason": "unsigned_artifact"})
                continue
            if sample.abi_profile != "compat_profile_v2":
                issues.append({"app_id": sample.app_id, "reason": "abi_profile_mismatch"})
                continue
            if not sample.deterministic:
                issues.append(
                    {"app_id": sample.app_id, "reason": "non_deterministic_result"}
                )
                continue

            tier_bucket = buckets[sample.tier]
            tier_bucket["eligible"] += 1
            if sample.passed:
                tier_bucket["passed"] += 1

        tier_reports = {}
        tier_pass = True
        for tier, stats in buckets.items():
            threshold = self.thresholds[tier]
            eligible = stats["eligible"]
            passed = stats["passed"]
            pass_rate = passed / eligible if eligible else 0.0
            meets = (
                eligible >= threshold["min_samples"]
                and pass_rate >= threshold["min_pass_rate"]
            )
            tier_reports[tier] = {
                "eligible": eligible,
                "passed": passed,
                "pass_rate": pass_rate,
                "min_samples": threshold["min_samples"],
                "min_pass_rate": threshold["min_pass_rate"],
                "meets_threshold": meets,
            }
            tier_pass = tier_pass and meets

        issues_sorted = sorted(issues, key=lambda item: (item["reason"], item["app_id"]))
        payload = {"tiers": tier_reports, "issues": issues_sorted}
        digest = sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

        return {
            "schema": "rugo.external_app_tier_report.v2",
            "gate_pass": tier_pass and not issues_sorted,
            "tiers": tier_reports,
            "issues": issues_sorted,
            "digest": digest,
        }
