# OCI Integration

The MVP runs in demo mode without OCI credentials. OCI-specific code is isolated in:

```text
backend/app/providers/oci_responses.py
```

## Configuration

Copy `.env.example` to `.env` locally and set values outside git:

```env
APP_ENV=oci
OCI_REGION=
OCI_COMPARTMENT_ID=
OCI_PROJECT_ID=
OCI_GENAI_ENDPOINT=
```

Do not commit `.env`, OCI config files, private keys, tokens, or real customer data.

## Adapter Boundary

The application depends on `LLMProvider`:

```text
AgentRunner -> LLMProvider -> MockLLMProvider or OCIResponsesProvider
```

Provider-specific request construction, authentication, retries, and response parsing belong only
inside the OCI adapter. The agent, tools, retrieval layer, and API should not import OCI SDK
objects directly.

## Current MVP Behavior

`OCIResponsesProvider` validates required settings and raises `NotImplementedError` for generation.
This is intentional. Implement the API call only from official OCI Responses API documentation or
SDK examples.

## Future Work

- Add official OCI client dependency.
- Implement request and response mapping.
- Add integration tests using mocked OCI client responses.
- Add OCI Files ingestion for synthetic policy documents.
- Add OCI Vector Stores retrieval behind the existing `Retriever` interface.
- Add MCP read-only database access only after schema and query permissions are defined.
