# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

| Action | Command |
|---|---|
| All checks | `make all` (lint + typecheck + test) |
| Lint | `uv run ruff check rag_system/ tests/` |
| Format | `uv run ruff format rag_system/ tests/` |
| Typecheck | `uv run mypy --strict --no-warn-unused-ignores -p rag_system` |
| Unit tests | `uv run pytest tests/unit/` |
| Integration tests | `uv run pytest tests/integration/` |
| Single test | `uv run pytest tests/unit/service/test_ingestion_service.py::TestIngestionService::test_ingest_document` |
| Pre-commit | `uv run pre-commit run --all-files` |
| Docker up/down | `make up` / `make down` |
| Frontend dev | `cd frontend && npm run dev` |
| Frontend checks | `cd frontend && npm run typecheck && npm run lint` |

## Architecture

Hexagonal (ports & adapters) — the domain never imports from adapters.

```
rag_system/
├── domain/
│   ├── model/          ← dataclasses: Document, Chunk, Query, Embedding, SearchResult
│   ├── port/inbound/   ← ABCs: QueryUseCase, IngestionUseCase
│   ├── port/outbound/  ← ABCs: EmbedderPort, RetrieverPort, LLMPort, DocumentStorePort, RerankerPort
│   └── service/        ← QueryService, IngestionService (inject ports via __init__)
├── adapter/
│   ├── inbound/api/    ← FastAPI router.py + Pydantic schemas.py
│   ├── inbound/cli/    ← Typer CLI for batch ingestion
│   └── outbound/       ← OpenRouterEmbedder, OpenRouterLLM, QdrantRetriever,
│                          PostgresDocumentStore, InMemoryRetriever (test stub)
└── config/
    ├── settings.py     ← pydantic-settings reads .env
    └── container.py    ← DI: lazy singleton @property for each port + service
```

**Data flow — Query**: `POST /query` → `QueryService.query()` → embed → vector search → optional rerank → LLM generate
**Data flow — Ingest**: `POST /ingest` → `IngestionService.ingest()` → chunk → embed_batch → store in Postgres + Qdrant

## Key conventions

- **DI container** (`config/container.py`): lazy singleton `@property` for every port. To swap an adapter, replace the relevant property. The reranker is wired but disabled by default (`use_reranker = False`).
- **Settings alias mismatch**: `settings.openrouter_llm_model` reads the env var `OPENROUTER_MODEL` (not `OPENROUTER_LLM_MODEL`).
- **Postgres**: schema auto-migrates on first connection via `PostgresDocumentStore.__aenter__`.
- **`InMemoryRetriever`**: word-overlap scorer, not vector-based — for tests only, not production.
- **pytest**: `asyncio_mode = auto` is set — never add `@pytest.mark.asyncio`.
- **Unit tests**: mock all ports with `AsyncMock` directly, not via `Container`. See `tests/unit/service/` for the pattern.
- **Integration tests**: require Qdrant + Postgres running locally; they skip gracefully on 401 if the API key is absent.
- **Auth**: if `API_KEY` env var is set, all endpoints require `Authorization: Bearer <key>`. Leave it empty to disable.

## Infrastructure

Four Docker services: `app` (uvicorn :8000), `frontend` (Next.js :3000), `qdrant` (:6333), `postgres` (:5432).

**Frontend** (`frontend/`): Next.js 15, Tailwind CSS v4, Radix UI, next-auth. Calls the backend via `lib/api/client.ts`.
