"""Pytest configuration and fixtures."""
import pytest
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test environment variables
os.environ["TESTING"] = "true"
os.environ["VIRUSTOTAL_API_KEY"] = "test_key"
os.environ["ABUSEIPDB_API_KEY"] = "test_key"
os.environ["OTX_API_KEY"] = "test_key"
os.environ["IPQS_API_KEY"] = "test_key"
os.environ["GREYNOISE_API_KEY"] = "test_key"


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("VIRUSTOTAL_API_KEY", "test_key")
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "test_key")
    monkeypatch.setenv("OTX_API_KEY", "test_key")
    monkeypatch.setenv("IPQS_API_KEY", "test_key")
    monkeypatch.setenv("GREYNOISE_API_KEY", "test_key")
    return True


@pytest.fixture
def sample_features():
    """Sample feature dictionary for testing."""
    return {
        "bytes": 1500.0,
        "pkts": 10.0,
        "iat_avg": 0.1,
        "iat_std": 0.05,
        "iat_max": 0.2,
        "iat_min": 0.01
    }


@pytest.fixture
def sample_ip():
    """Sample IP address for testing."""
    return "8.8.8.8"
