# CodeLens

**CodeLens** is a production-grade Codebase Intelligence and Developer Copilot platform. It allows developers to connect GitHub repositories, indexing and analyzing source code to build semantic and structural representations. This enables natural-language queries against the codebase, grounded in AST parsing, dependency analysis, and hybrid retrieval.

## Features

- **Code-Aware RAG:** Hybrid retrieval (Semantic + Keyword) with reranking to provide high-quality context.
- **Structural Analysis:** Uses Tree-sitter to parse ASTs and extract symbols, dependencies, and APIs.
- **Local First LLM:** Default integration with Ollama (e.g., qwen3:8b), with configurable support for OpenAI, Gemini, etc.
- **Interactive UI:** Developer-focused dark mode UI with React, Monaco Editor, and React Flow dependency graphs.
- **Citation Validation:** Grounded responses citing exact files and lines (e.g., `RideService.java:120-180`).
- **Incremental Indexing:** GitHub webhook integration to only re-index changed code using Kafka for background processing.
- **Observability:** Built-in Prometheus metrics, Grafana dashboards, and OpenTelemetry tracing.

## Architecture

CodeLens is divided into several components:

1. **Frontend:** React + TypeScript + Vite + Tailwind CSS.
2. **Backend:** FastAPI + Python (async).
3. **Database:** PostgreSQL for relational data (users, repositories, metadata, caching).
4. **Cache:** Redis for rate limiting, caching, and locks.
5. **Vector Database:** Qdrant for semantic chunk storage.
6. **Message Broker:** Kafka (KRaft mode) for background indexing workers.
7. **LLM Runtime:** Ollama (default) and LiteLLM abstraction.

## Tech Stack

- **Frontend:** React, TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand, Monaco Editor.
- **Backend:** Python 3.12, FastAPI, Pydantic, SQLAlchemy 2, asyncpg, Alembic.
- **AI/ML:** Qdrant, LangChain (minimal use), LiteLLM, Sentence Transformers.
- **Code Analysis:** Tree-sitter.
- **Infrastructure:** Docker, Docker Compose, Prometheus, Grafana.

## Local Setup (Phase 1)

1. Ensure you have Docker and Docker Compose installed.
2. Copy `.env.example` to `.env` and fill in the values.
3. Start the infrastructure:
   ```bash
   docker compose up -d
   ```
4. Check the status of the containers.

## Documentation

- [System Design](./docs/architecture/system-design.md)
- [Architecture Decision Records](./docs/decisions/)
