# System Design

## Overview
CodeLens is an AI-powered Codebase Intelligence platform.

```mermaid
graph TD
    UI[React Frontend] -->|REST / SSE| API[FastAPI Backend]
    API -->|Read/Write| DB[(PostgreSQL)]
    API -->|Cache / Rate Limit| Redis[(Redis)]
    API -->|Produce| Kafka[Kafka]
    Kafka -->|Consume| Worker[Background Worker]
    Worker -->|Index| Qdrant[(Qdrant Vector DB)]
    Worker -->|Parse| AST[Tree-sitter Parser]
    API -->|Search| Qdrant
    API -->|LLM Chat| LLM[LLM Provider / Ollama]
```

## RAG Pipeline
1. **Retrieve**: Semantic Search (Qdrant) + Keyword Search (PostgreSQL)
2. **Fuse**: Reciprocal Rank Fusion (RRF)
3. **Rerank**: Cross-Encoder Reranker
4. **Generate**: LLM with strict context grounding and citation generation
