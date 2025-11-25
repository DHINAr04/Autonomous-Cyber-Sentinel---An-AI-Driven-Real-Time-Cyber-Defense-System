import os
from typing import Dict, Iterator
from sentinel.common.config import capture_iface


class LiveCapture:
    def __init__(self) -> None:
        self._iface = capture_iface()

    def stream(self) -> Iterator[Dict[str, int | str | float]]:
        try:
            from scapy.all import sniff
            from scapy.layers.inet import IP
        except Exception:
            return iter(())

        def _pkt_to_evt(pkt) -> Dict[str, int | str | float]:
            if IP in pkt:
                ip = pkt[IP]
                size = int(len(pkt))
                ts = float(getattr(pkt, "time", __import__("time").time()))
                return {"src": ip.src, "dst": ip.dst, "proto": str(ip.proto), "size": size, "ts": ts}
            return {"src": "", "dst": "", "proto": "", "size": int(len(pkt)), "ts": float(__import__("time").time())}

        for pkt in sniff(iface=self._iface, filter="ip", store=False):
            yield _pkt_to_evt(pkt)