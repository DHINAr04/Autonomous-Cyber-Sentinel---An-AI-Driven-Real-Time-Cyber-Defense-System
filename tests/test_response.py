from sentinel.response.engine import ResponseEngine
from sentinel.common.event_bus import InMemoryEventBus
from sentinel.common.state import SharedState


def _engine():
    bus = InMemoryEventBus()
    state = SharedState()
    return ResponseEngine(bus, state)


def test_decision_matrix_high():
    eng = _engine()
    report = {"alert_id": "a1", "risk_score": 0.9, "verdict": "malicious", "alert_severity": "high", "confidence": 0.9}
    act = eng._decide(report)
    assert act.action_type in {"isolate_container", "block_ip", "rate_limit", "redirect_to_honeypot", "log_only"}
    assert act.reversible == "yes"
    assert act.reverted == "no"


def test_reversible_actions():
    eng = _engine()
    report = {"alert_id": "a2", "risk_score": 0.7, "verdict": "suspicious", "alert_severity": "medium", "confidence": 0.6}
    act = eng._decide(report)
    res = eng._handler.revert(act.action_type, act.target)
    assert res in {"reverted", "noop"}