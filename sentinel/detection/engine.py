import os
import threading
import random
import time
from typing import Optional
from sentinel.common.schemas import AlertEvent
from sentinel.common.event_bus import EventBus
from sentinel.common.state import SharedState
from .capture import LiveCapture
from sentinel.common.config import live_capture_enabled
from .batcher import MicroBatcher


class DetectionEngine:
    def __init__(self, bus: EventBus, state: SharedState, sensor_id: str) -> None:
        self.bus = bus
        self.state = state
        self.sensor_id = sensor_id
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._live = live_capture_enabled()
        self._capture: Optional[LiveCapture] = None

    def start(self) -> None:
        target = self._run_live if self._live else self._run_synthetic
        self._thread = threading.Thread(target=target, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _run_synthetic(self) -> None:
        while not self._stop.is_set():
            score = random.uniform(0.1, 1.0)
            alert = AlertEvent.synthetic(self.sensor_id, "10.0.0.5", "10.0.0.10", score)
            self.bus.publish("alerts", alert.to_dict())
            self.state.add_alert(alert.to_dict())
            time.sleep(1.0)

    def _run_live(self) -> None:
        self._capture = LiveCapture()
        batcher = MicroBatcher(self.sensor_id)
        for evt in self._capture.stream():
            if self._stop.is_set():
                break
            evt["ts"] = evt.get("ts") or __import__("time").time()
            alert = batcher.step(evt)
            if alert is None:
                continue
            self.bus.publish("alerts", alert.to_dict())
            self.state.add_alert(alert.to_dict())