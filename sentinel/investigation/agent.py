import threading
import time
from typing import Optional, Dict, Any
from sentinel.common.event_bus import EventBus
from sentinel.common.state import SharedState
from sentinel.common.event_bus import Subscriber
from sentinel.common.schemas import InvestigationReport
from .ti_clients import (
    VirusTotalClient,
    AbuseIPDBClient,
    OTXClient,
    IPQualityScoreClient,
    ThreatCrowdClient,
    GreyNoiseClient
)
from .cache import TTLCache, RedisTTLCache
from sentinel.common.config import redis_url


class InvestigationAgent:
    def __init__(self, bus: EventBus, state: SharedState) -> None:
        self.bus = bus
        self.state = state
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._sub = bus.subscribe("alerts")
        try:
            cache = RedisTTLCache(redis_url(), ttl=300.0)
        except Exception:
            cache = TTLCache(ttl=300.0)
        self._vt = VirusTotalClient(cache)
        self._abuse = AbuseIPDBClient(cache)
        self._otx = OTXClient(cache)
        self._ipqs = IPQualityScoreClient(cache)
        self._threatcrowd = ThreatCrowdClient(cache)
        self._greynoise = GreyNoiseClient(cache)

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _investigate(self, alert: Dict[str, Any]) -> InvestigationReport:
        score = float(alert.get("model_score", 0.5))
        src = alert.get("src_ip", "")
        
        # Query all TI sources
        vt = self._vt.ip_report(src)
        abuse = self._abuse.ip_check(src)
        otx = self._otx.ip_info(src)
        ipqs = self._ipqs.ip_check(src)
        threatcrowd = self._threatcrowd.ip_report(src)
        greynoise = self._greynoise.ip_check(src)
        
        # Calculate external risk from all sources
        ext_risk = 0.0
        ext_risk += float(vt.get("reputation", 0)) / 100.0
        ext_risk += float(abuse.get("abuse_score", 0)) / 100.0
        ext_risk += min(0.3, 0.1 * int(otx.get("pulses", 0)))
        ext_risk += float(ipqs.get("fraud_score", 0)) / 100.0
        ext_risk += min(0.2, 0.05 * int(threatcrowd.get("votes", 0)))
        
        # GreyNoise classification
        if greynoise.get("classification") == "malicious":
            ext_risk += 0.3
        elif greynoise.get("noise"):
            ext_risk += 0.1
        
        # Normalize risk score
        risk = min(1.0, max(0.0, 0.4 * score + 0.6 * (ext_risk / 6.0)))
        
        # Determine verdict
        verdict = "malicious" if risk >= 0.7 else ("suspicious" if risk >= 0.5 else "benign")
        
        # Compile findings
        findings = {
            "vt": vt,
            "abuseipdb": abuse,
            "otx": otx,
            "ipqualityscore": ipqs,
            "threatcrowd": threatcrowd,
            "greynoise": greynoise
        }
        
        sources = ["virustotal", "abuseipdb", "otx", "ipqualityscore", "threatcrowd", "greynoise"]
        
        # Calculate confidence based on mocked vs real data
        mocked_count = sum(1 for k in findings.values() if k.get("mocked", False))
        info_conf = 1.0 - (mocked_count / len(sources))
        alert_conf = float(alert.get("confidence", score))
        confidence = max(0.1, min(1.0, 0.5 * alert_conf + 0.5 * info_conf))
        uncertainty = max(0.0, 1.0 - info_conf)
        
        return InvestigationReport(
            alert_id=alert["id"],
            ts=time.time(),
            ioc_findings=findings,
            sources=sources,
            risk_score=risk,
            verdict=verdict,
            notes="automatic investigation with 6 TI sources",
            uncertainty=uncertainty,
            confidence=confidence,
            alert_severity=str(alert.get("severity", "low")),
        )

    def _run(self) -> None:
        while not self._stop.is_set():
            msg = self._sub.get(timeout=0.5)
            if msg is None:
                continue
            report = self._investigate(msg)
            self.bus.publish("investigations", report.to_dict())
            self.state.add_investigation(report.to_dict())