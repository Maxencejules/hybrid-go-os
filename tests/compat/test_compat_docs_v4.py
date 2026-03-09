"""M36 PR-1: compatibility profile v4 contract doc checks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_m36_pr1_compat_contract_artifacts_exist():
    required = [
        "docs/M36_EXECUTION_BACKLOG.md",
        "docs/abi/compat_profile_v4.md",
        "docs/runtime/syscall_coverage_matrix_v3.md",
        "docs/abi/process_model_v3.md",
        "docs/abi/socket_family_expansion_v1.md",
        "tests/compat/test_compat_docs_v4.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M36 PR-1 artifact: {rel}"


def test_compat_profile_v4_doc_declares_required_tokens():
    doc = _read("docs/abi/compat_profile_v4.md")
    for token in [
        "Compatibility profile identifier: `rugo.compat_profile.v4`.",
        "Process model contract ID: `rugo.process_model.v3`.",
        "Socket family contract ID: `rugo.socket_family_expansion.v1`.",
        "POSIX gap report schema: `rugo.posix_gap_report.v1`.",
        "Compatibility surface campaign schema: `rugo.compat_surface_campaign_report.v1`.",
        "Local gate: `make test-compat-surface-v1`.",
        "Local sub-gate: `make test-posix-gap-closure-v1`.",
        "CI gate: `Compatibility surface v1 gate`.",
        "CI sub-gate: `POSIX gap closure v1 gate`.",
    ]:
        assert token in doc


def test_syscall_coverage_matrix_v3_doc_declares_required_tokens():
    doc = _read("docs/runtime/syscall_coverage_matrix_v3.md")
    for token in [
        "Milestone: M36 Compatibility Surface Expansion v1",
        "`waitid`",
        "`pselect`",
        "`ppoll`",
        "`sendmsg`",
        "`recvmsg`",
        "`socketpair`",
        "`AF_UNIX` subset",
        "`AF_NETLINK` / raw packet parity",
        "compatibility surface gate | `test-compat-surface-v1`",
        "posix sub-gate | `test-posix-gap-closure-v1`",
    ]:
        assert token in doc


def test_process_model_v3_doc_declares_required_tokens():
    doc = _read("docs/abi/process_model_v3.md")
    for token in [
        "Process model contract ID: `rugo.process_model.v3`",
        "Parent compatibility profile ID: `rugo.compat_profile.v4`",
        "Surface campaign schema: `rugo.compat_surface_campaign_report.v1`",
        "`process_spawn_exec`",
        "`process_wait_reap_once`",
        "`process_signal_fifo`",
        "`process_sigkill_terminal`",
        "spawn-to-ready latency: `<= 140 ms`",
        "wait/reap latency: `<= 25 ms`",
    ]:
        assert token in doc


def test_socket_family_expansion_v1_doc_declares_required_tokens():
    doc = _read("docs/abi/socket_family_expansion_v1.md")
    for token in [
        "Socket family contract ID: `rugo.socket_family_expansion.v1`",
        "Parent compatibility profile ID: `rugo.compat_profile.v4`",
        "Surface campaign schema: `rugo.compat_surface_campaign_report.v1`",
        "`socket_af_inet_stream`",
        "`socket_af_inet6_dgram`",
        "`socket_af_unix_stream`",
        "`socket_af_unix_dgram`",
        "`sendmsg`",
        "`recvmsg`",
        "`socketpair`",
        "`AF_NETLINK`",
    ]:
        assert token in doc


def test_m35_m39_roadmap_anchor_declares_m36_gates():
    roadmap = _read("docs/M35_M39_GENERAL_PURPOSE_EXPANSION_ROADMAP.md")
    assert "test-compat-surface-v1" in roadmap
    assert "test-posix-gap-closure-v1" in roadmap
