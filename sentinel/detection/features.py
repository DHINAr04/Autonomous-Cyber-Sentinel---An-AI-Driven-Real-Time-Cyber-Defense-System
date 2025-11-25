import time
from typing import Dict, Tuple, Optional


FlowKey = Tuple[str, str, str]


class FlowStats:
    def __init__(self) -> None:
        self.bytes_total = 0
        self.pkts_total = 0
        self.last_ts: Optional[float] = None
        self.iat_sum = 0.0
        self.iat_count = 0

    def update(self, size: int, ts: Optional[float] = None) -> None:
        self.bytes_total += int(size)
        self.pkts_total += 1
        now = ts if ts is not None else time.time()
        if self.last_ts is not None:
            dt = max(0.0, float(now - self.last_ts))
            self.iat_sum += dt
            self.iat_count += 1
        self.last_ts = now

    def features(self) -> Dict[str, float]:
        iat_avg = (self.iat_sum / self.iat_count) if self.iat_count > 0 else 0.0
        return {
            "bytes": float(self.bytes_total),
            "pkts": float(self.pkts_total),
            "iat_avg": float(iat_avg),
        }


class FeatureExtractor:
    def __init__(self) -> None:
        self._flows: Dict[FlowKey, FlowStats] = {}

    def step(self, src: str, dst: str, proto: str, size: int, ts: Optional[float] = None) -> FlowStats:
        key: FlowKey = (src, dst, proto)
        stats = self._flows.get(key)
        if stats is None:
            stats = FlowStats()
            self._flows[key] = stats
        stats.update(size, ts)
        return stats

    def get(self, src: str, dst: str, proto: str) -> Optional[FlowStats]:
        return self._flows.get((src, dst, proto))

    def reset(self, src: str, dst: str, proto: str) -> None:
        self._flows.pop((src, dst, proto), None)