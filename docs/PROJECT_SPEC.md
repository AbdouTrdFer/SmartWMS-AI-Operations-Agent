# SmartWMS AI Operations Agent Project Specification

Build a portfolio-grade AI operations assistant for a Warehouse Management System. The system is
an AI intelligence layer on top of a small realistic WMS domain, not a complete WMS.

Core MVP use cases:
- Inventory analysis with structured read-only tools
- Reorder recommendation with clear facts and recommendations
- WMS policy Q&A through synthetic RAG documents
- Open order and backlog review
- Operational diagnosis from structured data plus policy context

MVP acceptance criteria:
- User can ask WMS questions from a web UI.
- Backend exposes `/api/v1/chat` and `/api/v1/health`.
- Agent calls read-only WMS tools.
- Agent retrieves synthetic policy documents.
- Invalid tool arguments are rejected.
- UI shows answers, tools, and sources.
- Project runs without OCI credentials in demo mode.
