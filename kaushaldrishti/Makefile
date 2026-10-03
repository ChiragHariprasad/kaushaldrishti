.PHONY: demo test refresh backtest export clean lint setup

# ─── Configuration ───────────────────────────────────────────
COMPOSE := docker compose
PYTHON  := python
PYTEST  := python -m pytest
API_URL := http://localhost:8000

# ─── Primary Targets ────────────────────────────────────────

## Start the full stack (database, API, frontend, nginx)
demo:
	@echo "╔══════════════════════════════════════════╗"
	@echo "║     KaushalDrishti — Starting Demo       ║"
	@echo "╚══════════════════════════════════════════╝"
	$(COMPOSE) up --build -d
	@echo ""
	@echo "Waiting for services..."
	@timeout /t 10 /nobreak >nul 2>&1 || sleep 10
	@echo ""
	@echo "✓ Dashboard:  http://localhost:80"
	@echo "✓ API:        http://localhost:8000"
	@echo "✓ API Docs:   http://localhost:8000/api/v1/docs"
	@echo "✓ Database:   localhost:5432"
	@echo ""
	@echo "Golden Path: National → Karnataka → District → Automotive → EV Service Technician"

## Run all tests (backend unit + integration, frontend playwright + axe)
test:
	@echo "Running backend tests..."
	cd backend && $(PYTEST) tests/ -v --tb=short
	@echo ""
	@echo "Running frontend tests..."
	cd frontend && npm test

## Refresh data pipeline (ingest, taxonomy, signals, demand, supply, gap, alerts)
refresh:
	@echo "Running data refresh pipeline..."
	cd backend && $(PYTHON) -m pipelines.refresh

## Run backtests and generate reports
backtest:
	@echo "Running backtests..."
	cd backend && $(PYTHON) scripts/backtest.py
	@echo "Results written to docs/ and database."

## Export data to local folder
export:
	@echo "Exporting data..."
	cd backend && $(PYTHON) scripts/export.py
	@echo "Exports written to data/exports/"

# ─── Development Helpers ─────────────────────────────────────

## Set up local development environment
setup:
	cd backend && pip install -e ".[dev]"
	cd frontend && npm install

## Lint and type-check
lint:
	cd backend && ruff check . && mypy app/ pipelines/
	cd frontend && npm run lint && npx tsc --noEmit

## Stop all services
down:
	$(COMPOSE) down

## Stop and remove volumes
clean:
	$(COMPOSE) down -v
	@echo "Cleaned up all containers and volumes."

## View logs
logs:
	$(COMPOSE) logs -f

## Run database migrations
migrate:
	cd backend && alembic upgrade head

## Seed reference data
seed:
	cd backend && $(PYTHON) scripts/seed.py

## Generate synthetic data
synth:
	cd backend && $(PYTHON) -m synth.generate

## Export OpenAPI spec
openapi:
	cd backend && $(PYTHON) scripts/export_openapi.py
