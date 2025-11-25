"""Integration tests for individual components."""
import pytest
from sentinel.detection.features import FeatureExtractor, FlowStats
from sentinel.detection.model import ModelRunner
from sentinel.investigation.ti_clients import VirusTotalClient, AbuseIPDBClient, OTXClient
from sentinel.investigation.cache import TTLCache
from sentinel.response.actions import ActionHandler
import time


def test_feature_extraction():
    """Test network traffic feature extraction."""
    extractor = FeatureExtractor()
    
    # Simulate packet flow
    stats = extractor.step("10.0.0.1", "10.0.0.2", "tcp", 1500, time.time())
    stats = extractor.step("10.0.0.1", "10.0.0.2", "tcp", 1500, time.time() + 0.1)
    stats = extractor.step("10.0.0.1", "10.0.0.2", "tcp", 1500, time.time() + 0.2)
    
    features = stats.features()
    
    assert features["bytes"] == 4500
    assert features["pkts"] == 3
    assert features["iat_avg"] > 0


def test_model_scoring():
    """Test threat scoring model."""
    runner = ModelRunner()
    
    # Test with suspicious features
    features = {"bytes": 15000.0, "pkts": 150.0, "iat_avg": 0.01}
    result = runner.score(features)
    
    assert "score" in result
    assert "severity" in result
    assert "confidence" in result
    assert 0 <= result["score"] <= 1
    assert result["severity"] in ["low", "medium", "high"]


def test_threat_intelligence_caching():
    """Test TI client caching mechanism."""
    cache = TTLCache(ttl=5.0)
    client = VirusTotalClient(cache)
    
    # First call (should cache)
    result1 = client.ip_report("8.8.8.8")
    
    # Second call (should hit cache)
    result2 = client.ip_report("8.8.8.8")
    
    assert result1 == result2
    assert result1.get("mocked") is True  # In offline mode


def test_action_handler():
    """Test response action execution."""
    handler = ActionHandler()
    
    # Test isolation
    result = handler.isolate_container("container://test", {"reason": "malicious"})
    assert "simulated" in result
    
    # Test revert
    revert_result = handler.revert("isolate_container", "container://test")
    assert revert_result == "reverted"


def test_cache_ttl_expiration():
    """Test that cache entries expire after TTL."""
    cache = TTLCache(ttl=1.0)
    
    cache.set("test-key", {"value": "test"}, 1.0)
    
    # Should exist immediately
    assert cache.get("test-key") is not None
    
    # Wait for expiration
    time.sleep(1.5)
    
    # Should be expired
    assert cache.get("test-key") is None


def test_multiple_ti_sources():
    """Test integration with multiple threat intelligence sources."""
    cache = TTLCache()
    
    vt = VirusTotalClient(cache)
    abuse = AbuseIPDBClient(cache)
    otx = OTXClient(cache)
    
    ip = "1.2.3.4"
    
    vt_result = vt.ip_report(ip)
    abuse_result = abuse.ip_check(ip)
    otx_result = otx.ip_info(ip)
    
    assert "reputation" in vt_result
    assert "abuse_score" in abuse_result
    assert "pulses" in otx_result
