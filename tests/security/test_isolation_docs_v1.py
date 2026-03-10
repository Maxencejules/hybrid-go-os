"""M42 PR-1: isolation and namespace/cgroup contract doc checks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_m42_pr1_isolation_contract_artifacts_exist():
    required = [
        "docs/M42_EXECUTION_BACKLOG.md",
        "docs/abi/namespace_cgroup_contract_v1.md",
        "docs/security/isolation_profile_v1.md",
        "docs/runtime/resource_control_policy_v1.md",
        "tests/security/test_isolation_docs_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing M42 PR-1 artifact: {rel}"


def test_namespace_cgroup_contract_doc_declares_required_tokens():
    doc = _read("docs/abi/namespace_cgroup_contract_v1.md")
    for token in [
        "Namespace/cgroup contract ID: `rugo.namespace_cgroup_contract.v1`.",
        "Isolation profile ID: `rugo.isolation_profile.v1`.",
        "Resource control policy ID: `rugo.resource_control_policy.v1`.",
        "Isolation campaign schema: `rugo.isolation_campaign_report.v1`.",
        "Resource control report schema: `rugo.resource_control_report.v1`.",
        "Local gate: `make test-isolation-baseline-v1`.",
        "Local sub-gate: `make test-namespace-cgroup-v1`.",
        "CI gate: `Isolation baseline v1 gate`.",
        "CI sub-gate: `Namespace cgroup v1 gate`.",
    ]:
        assert token in doc


def test_isolation_profile_doc_declares_required_tokens():
    doc = _read("docs/security/isolation_profile_v1.md")
    for token in [
        "Isolation profile ID: `rugo.isolation_profile.v1`",
        "Parent namespace/cgroup contract ID: `rugo.namespace_cgroup_contract.v1`",
        "Isolation campaign schema: `rugo.isolation_campaign_report.v1`",
        "`namespace_pid_isolation_ratio`",
        "`namespace_mount_isolation_ratio`",
        "`escape_setns_denied_ratio`",
        "`escape_cross_tenant_signal_denied_ratio`",
        "`escape_mount_propagation_block_ratio`",
        "setns denial ratio: `>= 1.0`",
        "privilege-escalation events: `<= 0`",
    ]:
        assert token in doc


def test_resource_control_policy_doc_declares_required_tokens():
    doc = _read("docs/runtime/resource_control_policy_v1.md")
    for token in [
        "Resource control policy ID: `rugo.resource_control_policy.v1`",
        "Parent namespace/cgroup contract ID: `rugo.namespace_cgroup_contract.v1`",
        "Resource control report schema: `rugo.resource_control_report.v1`",
        "Requirement schema: `rugo.resource_control_requirement_set.v1`",
        "`cpu_hard_quota_enforcement_ratio`",
        "`memory_hard_limit_enforcement_ratio`",
        "`io_bw_cap_enforcement_ratio`",
        "`pids_max_enforcement_ratio`",
        "`controller_drift_events`",
        "Local gate: `make test-isolation-baseline-v1`",
        "Local sub-gate: `make test-namespace-cgroup-v1`",
    ]:
        assert token in doc


def test_m40_m44_roadmap_anchor_declares_m42_gates():
    roadmap = _read("docs/M40_M44_GENERAL_PURPOSE_PARITY_ROADMAP.md")
    assert "test-isolation-baseline-v1" in roadmap
    assert "test-namespace-cgroup-v1" in roadmap
