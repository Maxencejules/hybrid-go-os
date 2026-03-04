"""Compatibility profile skeleton helpers for M8 PR-1."""

import os
from pathlib import Path

import pytest

STRICT_COMPAT_ENV = "RUGO_COMPAT_STRICT"
REPO_ROOT = Path(__file__).resolve().parents[2]


def _compat_todo(requirement):
    message = (
        f"TODO(M8): {requirement}. "
        f"Set {STRICT_COMPAT_ENV}=1 to treat compatibility TODOs as failures."
    )
    if os.environ.get(STRICT_COMPAT_ENV) == "1":
        pytest.fail(message)
    pytest.skip(message)


@pytest.fixture
def compat_todo():
    """Return the deterministic TODO gate used by compatibility skeleton tests."""
    return _compat_todo


def _read_repo_file(relpath):
    return (REPO_ROOT / relpath).read_text(encoding="utf-8")


@pytest.fixture
def read_repo_file():
    """Read a repository file by relative path."""
    return _read_repo_file
