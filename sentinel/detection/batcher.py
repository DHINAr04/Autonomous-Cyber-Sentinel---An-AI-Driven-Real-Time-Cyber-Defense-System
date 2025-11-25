import time
from typing import Optional, Dict, Any
from .features import FeatureExtractor
from .model import ModelRunner
from sentinel.common.schemas import AlertEvent


class MicroBatcher:
    def __init__(self, sensor_id: str, pkt_threshold: int = 10, bytes_threshold: int = 20000) -> None:
        self.sensor_id = sensor_id
        self._pkt_th = int(pkt_threshold)
        self._bytes_th = int(bytes_threshold)
        self._fe = FeatureExtractor()
        self._runner = ModelRunner()

    def step(self, evt: Dict[str, Any]) -> Optional[AlertEvent]:
        src = str(evt.get("src", ""))
        dst = str(evt.get("dst", ""))
        proto = str(evt.get("proto", ""))
        size = int(evt.get("size", 0))
        ts = float(evt.get("ts", time.time()))
        stats = self._fe.step(src, dst, proto, size, ts)
        feats = stats.features()
        if feats["pkts"] >= self._pkt_th or feats["bytes"] >= self._bytes_th:
            r = self._runner.score(feats)
            alert = AlertEvent(
                id=str(int(ts * 1000000)),
                ts=ts,
                src_ip=src,
                dst_ip=dst,
                proto=proto or "ip",
                features={"bytes": feats["bytes"], "pkts": feats["pkts"], "iat_avg": feats["iat_avg"]},
                model_score=r["score"],
                confidence=r["confidence"],
                severity=r["severity"],
                sensor_id=self.sensor_id,
            )
            self._fe.reset(src, dst, proto)
            return alert
        return None