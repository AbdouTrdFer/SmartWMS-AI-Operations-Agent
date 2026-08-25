# Technical Context

MVP stack:
- Backend: Python 3.12+, FastAPI, Pydantic, SQLAlchemy, pytest
- Frontend: Next.js, TypeScript, Tailwind CSS
- Database: PostgreSQL-compatible repository layer with SQLite demo fallback
- AI: provider-neutral interfaces, MockLLMProvider, OCI Responses API adapter skeleton

Environment variables:
- APP_ENV
- DATABASE_URL
- CHAT_MESSAGE_MAX_LENGTH
- OCI_REGION
- OCI_COMPARTMENT_ID
- OCI_PROJECT_ID
- OCI_GENAI_ENDPOINT

Never commit credentials, private keys, `.env` files, OCI config, or real customer data.
