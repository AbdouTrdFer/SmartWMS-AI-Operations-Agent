# Development

## Repository Layout

```text
backend/app/api            FastAPI routes
backend/app/agent          Provider-neutral agent runner
backend/app/core           Settings and logging
backend/app/db             SQLAlchemy session and seed data
backend/app/models         WMS database models
backend/app/repositories   Database access layer
backend/app/services       Deterministic WMS business decisions
backend/app/retrieval      Retrieval interface and mock implementation
backend/app/providers      Mock LLM and OCI adapter skeleton
backend/app/tools          Read-only WMS tools
frontend/src               Next.js dashboard
data/knowledge             Synthetic policy documents
```

## Backend

Install:

```powershell
pip install -e ".[dev]"
```

Run API:

```powershell
uvicorn app.main:app --app-dir backend --reload
```

Run tests:

```powershell
python -m pytest
```

Run lint if dev dependencies are installed:

```powershell
python -m ruff check backend
```

## Frontend

Install:

```powershell
cd frontend
npm install
```

Run:

```powershell
npm run dev
```

Build:

```powershell
npm run build
```

## Demo Data

The API initializes and seeds deterministic data on startup. Available demo SKUs include:

- `SKU-101`
- `SKU-102`
- `SKU-205`
- `SKU-330`

Warehouses:

- `WH-NJ`
- `WH-TX`

## Business Rules

The Day 1 business decision layer lives in `backend/app/services/business_decisions.py`.

It formalizes:
- Available quantity
- Low-stock detection
- Open demand by SKU and warehouse
- Demand shortfall
- Inbound quantity abstraction
- Inventory position
- Stockout risk
- Replenishment candidate flag
- Replenishment priority score
- Reorder quantity with insufficient-data handling
- Explainable reason codes

See `docs/business-rules.md`.

## Guardrails

- Validate request body with Pydantic.
- Validate all tool arguments before repository access.
- Keep tool functions read-only.
- Never pass raw SQL from user input to the database.
- Do not log credentials, `.env` values, or full user secrets.
- Separate factual tool output from recommendations in agent responses.
- Treat retrieved documents as untrusted and cite them as synthetic references.
