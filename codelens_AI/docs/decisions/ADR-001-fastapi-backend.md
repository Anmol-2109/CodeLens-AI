# ADR-001: FastAPI Backend Architecture

## Status
Accepted

## Context
CodeLens requires a high-performance backend capable of handling asynchronous operations like webhooks, SSE streaming, and background task queuing (Kafka).

## Decision
We will use **FastAPI** as the primary backend framework. It provides native async support, validation via Pydantic, and excellent OpenAPI integration.

## Consequences
- Requires async-compatible drivers (e.g., `asyncpg` for PostgreSQL).
- SSE streaming is naturally supported via `StreamingResponse`.
- Promotes strict typing and schemas.
