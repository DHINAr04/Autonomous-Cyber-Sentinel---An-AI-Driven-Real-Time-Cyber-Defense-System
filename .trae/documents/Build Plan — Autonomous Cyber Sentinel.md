## Goal
Transform the running MVP into a full, measurable prototype meeting the blueprint’s targets using only free tools.

## Phase A — Messaging, Config, Persistence
- Replace in-memory bus with Redis: add `redis` client, `RedisEventBus` implementation; env-driven switch (`BUS=redis|memory`).
- Config management: `.env` + `settings.yml` with env overrides; central loader in `sentinel/common`.
- Persistence: add `SQLite` via `SQLAlchemy` models for alerts, investigations, actions; write on publish.

## Phase B — Detection Engine (Live Traffic)
- Scapy capture: `sniff` with BPF filters; producer-consumer queue; graceful shutdown.
- Streaming features: per-flow rolling stats, inter-arrival times, protocol metadata; micro-batching for inference.
- Model artifacts: load `.joblib` model+scaler; thresholds from config; add unit tests for transformers.

## Phase C — Investigation Agent (Threat Intelligence)
- Clients: `VirusTotal`, `AbuseIPDB`, `OTX` wrappers with retry/backoff, rate-limiters, and Redis caching.
- Correlation: merge TI scores with internal context; compute `risk_score`; uncertainty flags for low confidence.
- Offline mode: mocked responses for testing; deterministic outputs for CI.

## Phase D — Response Engine (Safe Containment)
- Decision matrix: configurable mapping of severity × risk × confidence to actions.
- Docker Compose simulation: `lan`+`honeypot` networks; services `sensor`, `investigator`, `responder`, `dashboard`, `app1`, `db1`, `web1`.
- Actions: `isolate_container` (disconnect from network), `redirect_to_honeypot` (iptables/DNAT inside sim), `block_ip` (container-local firewall), `rate_limit` (tc rules), `quarantine_file` (simulated path ops); all reversible with audit log.

## Phase E — Dashboard & Observability
- FastAPI endpoints: filtering/paging; WebSocket `/stream` for live events.
- Metrics: `prometheus_client` counters/histograms; health and readiness endpoints.
- Structured logging: JSON logs; trace IDs; centralized view in dashboard.

## Phase F — Testing & CI/CD
- Unit tests: feature extraction, TI client wrappers, decision matrix.
- Integration tests: pipeline from alert → investigation → response using mocks.
- E2E tests: Compose spin-up, synthetic traffic, verify actions and SLA (<10s).
- CI: GitHub Actions job matrix: lint (`flake8`), security (`bandit`, `pip-audit`), tests, build images; cache deps.

## Deliverables & Verification
- Local run via `docker-compose up` showing autonomous detection, investigation, containment.
- API demo and dashboard with growing lists, metrics, and action audit.
- Metrics report meeting Accuracy/FPR goals and response time target.

## Implementation Order
1) Redis bus + config loader + SQLite persistence
2) Scapy streaming detection + model loading
3) TI integrations + caching + correlation
4) Response actions + Compose topology
5) Dashboard WS + metrics/logging
6) Tests + CI

## Ready to Execute
On your confirmation, I will implement Phase A → F sequentially, run the local server, and provide a preview URL and verification steps.