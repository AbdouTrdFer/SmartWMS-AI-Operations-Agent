# Architecture

```text
User -> Next.js Web App -> FastAPI -> Agent Runner
                                      |-> Read-only WMS Tools -> Business Decisions -> Repository -> DB
                                      |-> Mock Retriever -> Synthetic Knowledge
                                      |-> LLM Provider Interface -> Mock or OCI Adapter
```

Request lifecycle:
1. Frontend sends a validated chat request.
2. FastAPI validates message size and shape.
3. Agent decides whether tools, retrieval, or both are useful.
4. Agent calls only authorized read-only tool functions.
5. Tools use deterministic business decisions for inventory, demand, replenishment, and stockout
   facts.
6. Retrieved documents are treated as untrusted context.
7. Provider generates a grounded answer.
8. Response returns answer, tools used, sources, and conversation ID.

Design principle: start with one reliable agent and deterministic read-only tools. Add MCP,
vector stores, and multi-agent orchestration only after this foundation is stable.

Current business flow:

```text
WMS Data
  -> Repositories
  -> Domain Calculations
  -> Decision Engine
  -> Structured Results
  -> Future AI Agent
  -> LLM Explanation
```
