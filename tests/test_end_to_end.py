"""End-to-end integration tests for the Autonomous Cyber Sentinel."""
import pytest
import time
from sentinel.common.event_bus import InMemoryEventBus
from sentinel.common.state import SharedState
from sentinel.detection.engine import DetectionEngine
from sentinel.investigation.agent import InvestigationAgent
from sentinel.response.engine import ResponseEngine


@pytest.fixture
def setup_system():
    """Setup a complete system for testing."""
    bus = InMemoryEventBus()
    state = SharedState()
    detection = DetectionEngine(bus, state, sensor_id="test-sensor")
    investigator = InvestigationAgent(bus, state)
    responder = ResponseEngine(bus, state)
    
    yield bus, state, detection, investigator, responder
    
    # Cleanup
    detection.stop()
    investigator.stop()
    responder.stop()


def test_full_pipeline(setup_system):
    """Test the complete detection -> investigation -> response pipeline."""
    bus, state, detection, investigator, responder = setup_system
    
    # Start all components
    detection.start()
    investigator.start()
    responder.start()
    
    # Wait for synthetic alerts to be generated
    time.sleep(3)
    
    # Verify alerts were generated
    assert len(state.alerts) > 0, "No alerts generated"
    
    # Verify investigations were performed
    assert len(state.investigations) > 0, "No investigations performed"
    
    # Verify actions were taken
    assert len(state.actions) > 0, "No actions taken"
    
    # Verify data consistency
    alert = state.alerts[0]
    assert "id" in alert
    assert "severity" in alert
    assert alert["severity"] in ["low", "medium", "high"]
    
    investigation = state.investigations[0]
    assert "alert_id" in investigation
    assert "verdict" in investigation
    assert investigation["verdict"] in ["benign", "suspicious", "malicious"]
    
    action = state.actions[0]
    assert "action_type" in action
    assert "result" in action


def test_response_time_sla(setup_system):
    """Test that the system meets the <10 second response time SLA."""
    bus, state, detection, investigator, responder = setup_system
    
    detection.start()
    investigator.start()
    responder.start()
    
    start_time = time.time()
    
    # Wait for first complete cycle
    while len(state.actions) == 0 and (time.time() - start_time) < 15:
        time.sleep(0.1)
    
    elapsed = time.time() - start_time
    
    assert len(state.actions) > 0, "No actions taken within timeout"
    assert elapsed < 10, f"Response time {elapsed:.2f}s exceeds 10s SLA"


def test_event_bus_reliability(setup_system):
    """Test that events are reliably transmitted through the bus."""
    bus, state, _, _, _ = setup_system
    
    # Publish test event
    test_event = {"id": "test-123", "type": "test"}
    bus.publish("test-channel", test_event)
    
    # Subscribe and receive
    sub = bus.subscribe("test-channel")
    received = sub.get(timeout=1.0)
    
    assert received is not None
    assert received["id"] == "test-123"
