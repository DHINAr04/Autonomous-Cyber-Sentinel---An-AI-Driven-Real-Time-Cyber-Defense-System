import threading
from fastapi import FastAPI
import uvicorn
from sentinel.common.event_bus import BusFactory
from sentinel.common.state import SharedState
from sentinel.common.persistence import Repository
from sentinel.detection.engine import DetectionEngine
from sentinel.investigation.agent import InvestigationAgent
from sentinel.response.engine import ResponseEngine
from sentinel.dashboard.app import create_app


def main() -> None:
    repo = Repository()
    state = SharedState(repo=repo)
    bus = BusFactory.from_env()
    detection = DetectionEngine(bus, state, sensor_id="sensor-1")
    investigator = InvestigationAgent(bus, state)
    responder = ResponseEngine(bus, state)

    detection.start()
    investigator.start()
    responder.start()

    app: FastAPI = create_app(state)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()