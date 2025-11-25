import time
from sentinel.common.schemas import InvestigationReport
from sentinel.investigation.agent import InvestigationAgent
from sentinel.common.event_bus import InMemoryEventBus
from sentinel.common.state import SharedState


def test_investigation_uncertainty_offline(monkeypatch):
    monkeypatch.setenv("OFFLINE_MODE", "1")
    bus = InMemoryEventBus()
    state = SharedState()
    agent = InvestigationAgent(bus, state)
    alert = {
        "id": "a1",
        "ts": time.time(),
        "src_ip": "1.2.3.4",
        "dst_ip": "5.6.7.8",
        "proto": "tcp",
        "features": {"bytes": 5000.0, "pkts": 50.0, "iat_avg": 0.5},
        "model_score": 0.6,
        "confidence": 0.7,
        "severity": "medium",
        "sensor_id": "s1",
    }
    report = agent._investigate(alert)
    assert isinstance(report, InvestigationReport)
    assert 0.0 <= report.risk_score <= 1.0
    assert 0.0 <= report.uncertainty <= 1.0
    assert 0.1 <= report.confidence <= 1.0