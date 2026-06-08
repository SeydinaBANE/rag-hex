# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

| Action | Command |
|---|---|
| All checks | `make all` (lint + typecheck + unit tests) |
| Lint | `uv run ruff check rag_system/ tests/` |
| Format | `uv run ruff format rag_system/ tests/` |
| Typecheck | `uv run mypy --strict --no-warn-unused-ignores -p rag_system` |
| Unit tests | `uv run pytest tests/unit/ --cov=rag_system` |
| Integration tests | `uv run pytest tests/integration/` (nécessite Qdrant + Postgres en cours) |
| Single test | `uv run pytest tests/unit/service/test_ingestion_service.py::TestIngestionService::test_ingest_document` |
| Pre-commit | `uv run pre-commit run --all-files` |
| Docker up/down | `make up` / `make down` / `make logs` |
| Health / Readiness | `make health` / `make readiness` |
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
**Readiness**: `GET /readiness` → ping Postgres + Qdrant → 200 ou 503

## Key conventions

- **DI container** (`config/container.py`): lazy singleton `@property` for every port. `startup()` / `shutdown()` appelés via le lifespan FastAPI. Pour swapper un adapter, remplacer la property concernée.
- **Settings alias mismatch**: `settings.openrouter_llm_model` lit la var d'env `OPENROUTER_MODEL` (pas `OPENROUTER_LLM_MODEL`).
- **`ENVIRONMENT=production`**: active le fail-fast au démarrage si `OPENROUTER_API_KEY` est vide. Par défaut `development` — aucune validation stricte.
- **`ALLOWED_ORIGINS`**: var d'env pour le CORS (ex. `https://monsite.com`). Par défaut `http://localhost:3000`.
- **Ports ABCs** (`domain/port/outbound/`): tous exposent `ping() -> bool` et `close() -> None`. Les ajouter à toute nouvelle implémentation.
- **Typed exceptions**: les adapters lèvent `EmbeddingError`, `LLMError`, `RetrievalError` (héritent de `RagError` dans `domain/exceptions.py`). Les handlers FastAPI les mappent aux bons codes HTTP (502/503).
- **Auth**: si `API_KEY` est défini, tous les endpoints requièrent `Authorization: Bearer <key>`. Laisser vide pour désactiver. La comparaison utilise `secrets.compare_digest` (timing-safe).
- **Postgres**: auto-migre les tables au premier appel. `ping()` fait un `SELECT 1`.
- **`InMemoryRetriever`**: scoring par overlap de mots, pas vectoriel — tests uniquement, jamais en prod.
- **pytest**: `asyncio_mode = auto` — ne jamais ajouter `@pytest.mark.asyncio`.
- **Mocks Postgres store**: utiliser `MagicMock` pour le pool (appel synchrone) + `AsyncMock` pour le curseur. Voir `tests/unit/adapter/test_postgres_document_store.py`.
- **Integration tests**: nécessitent Qdrant + Postgres en local ; passent silencieusement sur 401 si la clé API est absente.

## Infrastructure

Four Docker services: `app` (uvicorn :8000), `frontend` (Next.js :3000), `qdrant` (:6333), `postgres` (:5432).

**Frontend** (`frontend/`): Next.js 15, Tailwind CSS v4, Radix UI, next-auth. Calls the backend via `lib/api/client.ts`.
