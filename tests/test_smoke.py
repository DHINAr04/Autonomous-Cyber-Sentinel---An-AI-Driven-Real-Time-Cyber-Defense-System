"""Smoke tests to verify basic functionality."""
import pytest


def test_imports():
    """Test that all main modules can be imported."""
    try:
        import sentinel
        import sentinel.detection
        import sentinel.investigation
        import sentinel.response
        import sentinel.dashboard
        import sentinel.reporting
        import sentinel.common
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_basic_math():
    """Sanity check that pytest is working."""
    assert 1 + 1 == 2
    assert 2 * 2 == 4


def test_python_version():
    """Verify Python version is compatible."""
    import sys
    version = sys.version_info
    assert version.major == 3
    assert version.minor >= 10, "Python 3.10+ required"
