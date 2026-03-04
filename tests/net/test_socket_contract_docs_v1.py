"""M12 acceptance: network/socket contract docs and gate wiring."""

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (_repo_root() / relpath).read_text(encoding="utf-8")


def test_m12_docs_tools_and_gate_wiring():
    root = _repo_root()
    required = [
        "docs/M12_EXECUTION_BACKLOG.md",
        "docs/net/network_stack_contract_v1.md",
        "docs/net/socket_contract_v1.md",
        "docs/net/ipv4_udp_profile_v1.md",
        "docs/net/tcp_state_machine_v1.md",
        "docs/net/retransmission_timer_policy_v1.md",
        "docs/net/ipv6_baseline_v1.md",
        "tools/net_trace_capture_v1.py",
        "tools/run_net_interop_matrix_v1.py",
        "tools/run_net_soak_v1.py",
    ]
    for rel in required:
        assert (root / rel).is_file(), f"missing M12 artifact: {rel}"

    net_contract = _read("docs/net/network_stack_contract_v1.md")
    socket_contract = _read("docs/net/socket_contract_v1.md")
    makefile = _read("Makefile")
    ci = _read(".github/workflows/ci.yml")

    assert "active release gate" in net_contract
    assert "`sys_net_send`" in net_contract
    assert "`sys_net_recv`" in net_contract
    assert "blocking and non-blocking semantics" in socket_contract.lower()
    assert "test-network-stack-v1" in makefile
    assert "Network stack v1 gate" in ci

