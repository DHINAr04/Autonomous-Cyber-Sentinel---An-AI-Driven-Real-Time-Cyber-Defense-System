## Current Phase
- Status: Pre-execution ("Ready to Execute"): waiting for your confirmation
- Next scheduled phase: Phase A — Messaging, Config, Persistence

## Phase A Scope
- Event bus: implement `RedisEventBus` with `BUS=redis|memory` env switch
- Config: centralized loader combining `.env` and `settings.yml` with env overrides
- Persistence: SQLite via SQLAlchemy for alerts, investigations, actions; write-on-publish

## Implementation Steps
1. Add Redis client and `RedisEventBus` behind existing bus interface; default to memory when unavailable
2. Introduce `sentinel/common/config.py` to load/merge `.env` and `settings.yml` with typed accessors
3. Create SQLAlchemy models and session factory; persist events on publish paths
4. Provide database init script and minimal seeds for local testing

## Verification
- Unit tests for config loader and bus (redis vs memory)
- Local run with `BUS=redis` shows events persisted to SQLite
- Logs include trace IDs verifying message → persistence flow

## Constraints & Security
- Use only free tools; do not hard-code secrets; read credentials from environment
- Keep dependencies minimal and consistent with existing code style

## Next Steps
- On approval, execute Phase A, then proceed sequentially through Phases B → F with short verification after each