## Autonomous Cyber Sentinel — Copilot instructions

This file gives targeted guidance for AI coding agents working on this repository. Keep suggestions concrete and repository-focused: reference files, follow existing patterns, and prefer minimal, test-backed changes.

- Project structure: core runtime lives under `sentinel/`. Key subpackages:
  - `sentinel/detection/` — flow capture, feature extraction, model scoring (`engine.py`, `features.py`, `model.py`).
  - `sentinel/investigation/` — enrichment and threat-intel clients, caching (`agent.py`, `ti_clients.py`, `cache.py`).
  - `sentinel/response/` — decision-making and action handlers (`engine.py`, `actions.py`).
  - `sentinel/common/` — config, event bus, persistence, shared state, schemas (`config.py`, `event_bus.py`, `persistence.py`, `state.py`, `schemas.py`).
  - `sentinel/dashboard/` — FastAPI app for observability (`app.py`).

- Big-picture dataflow (single-sentence): `DetectionEngine` publishes alerts -> `InvestigationAgent` subscribes and publishes investigations -> `ResponseEngine` subscribes and emits actions; `SharedState` and `Repository` persist items.

- Event bus patterns and conventions:
  - Channels: plain string channels are used: `"alerts"`, `"investigations"`, `"responses"` (see `sentinel/common/event_bus.py`).
  - Bus selection: use `BusFactory.from_env()` (reads `BUS` env or `settings.yml`) — supports `memory` (default) and `redis` (`REDIS_URL`) fallbacks.
  - Messages are Python dicts that map to dataclasses in `sentinel/common/schemas.py` (e.g., `AlertEvent.to_dict()`, `InvestigationReport.to_dict()`).

- Configuration sources and important env vars (see `sentinel/common/config.py`):
  - `settings.yml` (root) merged with environment variables.
  - BUS selection: `BUS` (`memory` | `redis`)
  - `REDIS_URL`, `SENTINEL_DB` (SQLAlchemy URI), `LIVE_CAPTURE`, `CAPTURE_IFACE`, `MODEL_PATH`, `VT_API_KEY`, `ABUSEIPDB_API_KEY`, `OTX_API_KEY`.

- Runtime & developer workflows:
  - Full system (engines + dashboard): run the top-level `sentinel/run.py` to start Detection, Investigation, Response and uvicorn app; or use the provided PowerShell helper `scripts/dev.ps1 run`.
  - Dashboard only (FastAPI): `scripts/dev.ps1 run` launches `uvicorn sentinel.dashboard.app:app`.
  - Tests: `scripts/dev.ps1 test` or `python -m pytest -q` (tests prefer `InMemoryEventBus` + `SharedState`).
  - Install deps: `scripts/dev.ps1 install` or `python -m pip install -r requirements.txt`.

- Project-specific conventions to follow in code suggestions:
  - Prefer the existing simple, defensive style: many modules catch exceptions and fall back (e.g., optional `joblib`, `redis` imports). Mirror that approach when adding integrations.
  - Use the event-bus publish/subscribe pattern: add new background work as an Engine class with `start()`/`stop()` methods and a thread; publish dicts and call `state.add_*()` to update `SharedState` and persistence.
  - Keep messages as plain serializable dicts (no complex objects) to remain compatible with `RedisEventBus`'s JSON payload handling.
  - Respect safety gates: decision logic is centralized in `sentinel/common/config.py` (`decision_matrix`) and applied in `sentinel/response/engine.py` — do not bypass without tests.

- Integration points and dependencies to be aware of:
  - Optional external services: VirusTotal, AbuseIPDB, OTX clients in `sentinel/investigation/ti_clients.py` (guarded by API key config).
  - Persistence: SQLAlchemy via `sentinel/common/persistence.py`; DB URL from `SENTINEL_DB`.
  - Optional model: `sentinel/detection/model.py` loads a joblib model when `MODEL_PATH` is set; otherwise falls back to the heuristic scorer.

- Tests & examples:
  - `tests/test_pipeline.py` demonstrates an integration-style test that uses `InMemoryEventBus()` and `SharedState()` to run `DetectionEngine`, `InvestigationAgent`, and `ResponseEngine` for a short time and asserts items were produced.
  - When adding features, follow the test pattern: use in-memory bus, short runtimes, and assert lists in `state.alerts`, `state.investigations`, `state.actions`.

- Where to look first when changing behavior:
  - routing/flow: `sentinel/common/event_bus.py`, `sentinel/common/schemas.py`
  - decision & safety: `sentinel/common/config.py`, `sentinel/response/engine.py`
  - core loops: `sentinel/detection/engine.py`, `sentinel/investigation/agent.py`
  - persistence: `sentinel/common/persistence.py`, `sentinel/common/state.py`

If any section here is unclear or you'd like extra examples (small PR-sized changes, tests, or a walkthrough of the model-loading path), tell me which area to expand and I'll iterate.
