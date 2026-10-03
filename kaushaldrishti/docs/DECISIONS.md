# Architecture and Design Decisions

This document records every non-obvious default chosen during implementation.

## M0 — Scaffold

| # | Decision | Rationale |
|---|----------|-----------|
| D-001 | SQLite fallback for unit tests | Avoids requiring PostgreSQL for CI/local testing. PostGIS-specific features tested only in integration. |
| D-002 | Nginx as reverse proxy on port 80 | Single entry point for the demo; API on /api/, frontend on /. |
| D-003 | `dev-key-2026` as default API key | Development convenience. Must be changed via `API_KEY` env var in production. |
| D-004 | Docker Compose v3.9 | Supports `service_healthy` condition for ordered startup. |
| D-005 | `pydantic-settings` for config | Type-safe env var loading with defaults, matching the Pydantic v2 ecosystem. |
