import threading
import time
from typing import Optional, Dict, Any
from sentinel.common.event_bus import EventBus
from sentinel.common.state import SharedState
from sentinel.common.event_bus import Subscriber
from sentinel.common.schemas import ResponseAction
from .actions import ActionHandler
from sentinel.common.config import decision_matrix


class ResponseEngine:
    def __init__(self, bus: EventBus, state: SharedState) -> None:
        self.bus = bus
        self.state = state
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._sub = bus.subscribe("investigations")
        self._handler = ActionHandler()

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _decide(self, report: Dict[str, Any]) -> ResponseAction:
        risk = float(report.get("risk_score", 0.5))
        verdict = report.get("verdict", "suspicious")
        severity = str(report.get("alert_severity", "low"))
        conf = float(report.get("confidence", 0.5))
        dm = decision_matrix()
        tier_risk = "high" if risk >= 0.8 else ("medium" if risk >= 0.6 else "low")
        tier_conf = "high" if conf >= 0.8 else ("medium" if conf >= 0.5 else "low")
        actions_for_sev = dm.get(severity, dm.get("low", {}))
        action_type = actions_for_sev.get("risk", {}).get(tier_risk, "log_only")
        safety = "high" if tier_risk == "high" or tier_conf == "high" else ("medium" if tier_risk == "medium" or tier_conf == "medium" else "low")
        params = {"verdict": verdict}
        # execute simulated actions
        if action_type == "isolate_container":
            result = self._handler.isolate_container("container://app1", params)
        elif action_type == "redirect_to_honeypot":
            result = self._handler.redirect_to_honeypot("container://app1", params)
        elif action_type == "block_ip":
            result = self._handler.block_ip("container://app1", params)
        elif action_type == "rate_limit":
            result = self._handler.rate_limit("container://app1", params)
        elif action_type == "quarantine_file":
            result = self._handler.quarantine_file("container://app1", params)
        else:
            result = "recorded"
        return ResponseAction(
            action_id=str(report["alert_id"]),
            alert_id=str(report["alert_id"]),
            ts=time.time(),
            action_type=action_type,
            target="container://app1",
            parameters=params,
            result=result,
            safety_gate=safety,
            reversible="yes",
            reverted="no",
        )

    def _run(self) -> None:
        while not self._stop.is_set():
            msg = self._sub.get(timeout=0.5)
            if msg is None:
                continue
            action = self._decide(msg)
            self.bus.publish("responses", action.to_dict())
            self.state.add_action(action.to_dict())