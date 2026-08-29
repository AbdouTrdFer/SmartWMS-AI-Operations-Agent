# SmartWMS AI Operations Agent Project Specification

Build a portfolio-grade AI operations assistant for a Warehouse Management System. The system is
an AI intelligence layer on top of a small realistic WMS domain, not a complete WMS.

Core MVP use cases:
- Inventory analysis with structured read-only tools
- Reorder recommendation with clear facts and recommendations
- WMS policy Q&A through synthetic RAG documents
- Open order and backlog review
- Operational diagnosis from structured data plus policy context

Day 1 business logic goal:
- Keep WMS decisions deterministic and testable outside the LLM.
- Centralize inventory, stockout, and reorder rules in the backend service layer.
- Expose facts and reason codes that a later agent can explain without inventing business logic.

MVP acceptance criteria:
- User can ask WMS questions from a web UI.
- Backend exposes `/api/v1/chat` and `/api/v1/health`.
- Agent calls read-only WMS tools.
- Agent retrieves synthetic policy documents.
- Invalid tool arguments are rejected.
- UI shows answers, tools, and sources.
- Project runs without OCI credentials in demo mode.

## Data and ML Engineering Fit

This project is primarily an agentic AI and enterprise application architecture project. Data
engineering belongs when preparing reliable warehouse datasets, validating schemas, building
ingestion pipelines, and creating retrieval-ready policy documents.

Machine learning engineering belongs later if the project adds embeddings, vector stores,
reranking, forecasting, anomaly detection, or model evaluation. The MVP should not claim real ML
training because it currently uses deterministic synthetic data and a mock LLM provider.

Suggested data path:
- Start with synthetic WMS data for repeatable demos.
- Add a documented raw-to-clean data pipeline for products, inventory, orders, suppliers, and stock
  movements.
- Validate data quality rules such as missing SKUs, negative inventory, invalid warehouses,
  duplicated orders, and stale stock movements.
- Load cleaned data through the repository layer.
- Add embeddings/vector retrieval only after the document pipeline is stable.
