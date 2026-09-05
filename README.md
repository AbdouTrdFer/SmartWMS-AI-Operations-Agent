# SmartWMS AI Operations Agent

Portfolio-grade MVP skeleton for an AI operations assistant on top of a Warehouse Management
System. The first release is intentionally read-only and runs in demo mode without OCI credentials.

## What It Does

- Answers WMS questions through `POST /api/v1/chat`
- Exposes `GET /api/v1/health`
- Uses deterministic synthetic WMS data for products, warehouses, inventory, orders, suppliers,
  and stock movements
- Computes deterministic business decisions for available quantity, open demand, inventory
  position, stockout risk, replenishment candidacy, replenishment priority, and reorder quantity
- Retrieves synthetic SOP/policy documents from `data/knowledge/`
- Shows a minimal Next.js chat dashboard with tools and sources used
- Keeps OCI-specific code isolated in `backend/app/providers/oci_responses.py`

## Architecture

```text
Next.js UI -> FastAPI -> Agent Runner
                       |-> read-only tools -> business decisions -> repository -> database
                       |-> mock retriever -> synthetic docs
                       |-> LLM provider interface -> mock provider or OCI adapter
```

The LLM never receives unrestricted database access. User input is validated, tool arguments are
validated, and retrieved documents are treated as untrusted context.

## Setup

Backend:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --app-dir backend --reload
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. The frontend expects the API at `http://localhost:8000` unless
`NEXT_PUBLIC_API_BASE_URL` is set.

## Demo Mode

Demo mode is the default:

```env
APP_ENV=demo
DATABASE_URL=sqlite:///./smartwms_demo.db
```

The backend creates and seeds a local SQLite database. The repository layer is SQLAlchemy-based so
the application can later point at PostgreSQL-compatible databases.

## OCI Mode

Set `APP_ENV=oci` only after adding a real OCI Responses API implementation. The MVP adapter checks
required configuration and then raises `NotImplementedError` for generation. It does not hardcode
credentials and does not invent OCI behavior.

See [OCI_INTEGRATION.md](docs/OCI_INTEGRATION.md).

## Example Questions

- Why is SKU-102 a high replenishment priority at WH-NJ?
- Show low stock items in WH-NJ.
- List open orders for WH-TX.
- What is the damaged goods procedure?
- What should we check during receiving?

## Security Notes

- MVP tools are read-only.
- No arbitrary SQL is exposed.
- Empty and oversized messages are rejected.
- Tool logging records tool names, not secrets or raw credential-like values.
- `.env`, keys, local databases, and build artifacts are ignored by git.
- Synthetic policy documents are fictional and must not be represented as real company policy.
- Reorder quantity is returned only when target stock and inbound data are available.
- Replenishment priority is a prototype deterministic heuristic, not a predictive ML model.

## Roadmap

- Professional UI polish for a clearer operations-console experience
- Documented data engineering pipeline for raw warehouse exports and cleaned demo datasets
- Business rules expansion for replenishment, order exceptions, and transfer recommendations
- OCI Responses API implementation using official documentation and SDK/client guidance
- OCI Files and Vector Stores integration
- MCP database access with approved read-only schemas
- Conversation memory design
- Specialist agents for inventory, orders, logistics, and policy once the single-agent workflow is
  stable

## Data Engineering vs ML Engineering

For this project, data engineering is directly relevant: collecting warehouse exports, cleaning
SKUs/orders/inventory, validating quality rules, and loading clean data for the agent tools.

ML engineering is a later phase: embeddings, vector stores, reranking, demand forecasting, anomaly
detection, and evaluation. The current MVP should be described as agentic AI with deterministic
demo data, not as a trained ML system.
