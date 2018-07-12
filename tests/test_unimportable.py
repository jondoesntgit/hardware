"""Tests whether a module will be skipped if an import fails."""

import pytest
try:
    from hardware import does_not_exist
except ImportError:
    pytestmark = pytest.mark.skip


def test_true():
    print("This should not be seen")
    assert False
