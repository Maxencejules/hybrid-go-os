"""Compatibility profile skeleton helpers for M8 PR-1."""

import os

import pytest

STRICT_COMPAT_ENV = "RUGO_COMPAT_STRICT"


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
