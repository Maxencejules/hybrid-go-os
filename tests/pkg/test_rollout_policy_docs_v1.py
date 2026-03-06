"""M33 acceptance: staged rollout policy docs are present."""

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (_repo_root() / relpath).read_text(encoding="utf-8").lower()


def test_rollout_policy_docs_v1_present():
    root = _repo_root()
    required = [
        "docs/pkg/staged_rollout_policy_v1.md",
        "docs/runtime/canary_slo_policy_v1.md",
        "tools/run_canary_rollout_sim_v1.py",
        "tools/run_rollout_abort_drill_v1.py",
    ]
    for rel in required:
        assert (root / rel).is_file(), f"missing M33 artifact: {rel}"

    rollout = _read("docs/pkg/staged_rollout_policy_v1.md")
    slo = _read("docs/runtime/canary_slo_policy_v1.md")
    assert "canary" in rollout
    assert "blast-radius" in rollout
    assert "automatic halt" in rollout
    assert "slo" in slo
    assert "rollback" in slo

