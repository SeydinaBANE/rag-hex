# rag-hex

[![Python](https://img.shields.io/badge/python-3.12+-blue?logo=python)](https://www.python.org)
[![Ruff](https://img.shields.io/badge/code_style-ruff-000000?logo=ruff)](https://docs.astral.sh/ruff)
[![Mypy](https://img.shields.io/badge/type_check-mypy_strict-2A6DB2?logo=python)](https://mypy-lang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js)](https://nextjs.org)
[![Qdrant](https://img.shields.io/badge/vector_store-Qdrant-EF3B2D)](https://qdrant.tech)
[![PostgreSQL](https://img.shields.io/badge/document_store-PostgreSQL-4169E1?logo=postgresql)](https://postgresql.org)
[![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-412991)](https://openrouter.ai)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

RAG system built with a hexagonal (ports & adapters) architecture — domain pure, adapters swappable, everything testable.

## Architecture

```
rag_system/
├── domain/              ← pure Python, zero external dependencies
│   ├── model/           ← dataclasses (Document, Chunk, Query, Embedding)
│   ├── port/inbound/    ← inbound ABCs (QueryUseCase, IngestionUseCase)
│   ├── port/outbound/   ← outbound ABCs (EmbedderPort, RetrieverPort, LLMPort, ...)
│   └── service/         ← business orchestration (QueryService, IngestionService)
├── adapter/
│   ├── inbound/api/     ← FastAPI routes + Pydantic schemas
│   ├── inbound/cli/     ← Typer CLI for batch ingestion
│   └── outbound/        ← concrete adapters (OpenRouter, Qdrant, PostgreSQL)
└── config/
    ├── settings.py      ← pydantic-settings (reads .env)
    └── container.py     ← DI container wiring everything
```

## Quick start

```sh
cp .env.example .env     # edit with your keys
uv sync                  # install deps
uv run pytest tests/unit/ -x  # fast verification
```

## Data flow

**Query**: `POST /query` → QueryService → embed → retrieve → (rerank) → LLM generate → response

**Ingestion**: `POST /ingest` → IngestionService → chunk → embed_batch → store (PostgreSQL + Qdrant)

## Commands

| Action | Command |
|---|---|
| Lint | `uv run ruff check rag_system/ tests/` |
| Format | `uv run ruff format rag_system/ tests/` |
| Typecheck | `uv run mypy --strict -p rag_system` |
| Test all | `uv run pytest tests/` |
| Test unit | `uv run pytest tests/unit/` |
| Test integ | `uv run pytest tests/integration/` |
| Pre-commit | `uv run pre-commit run --all-files` |
| All checks | `make all` |

## API

| Method | Route | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/query` | RAG query |
| POST | `/query/stream` | SSE streaming RAG query |
| POST | `/ingest` | Ingest a document |
| GET | `/documents` | List all documents |
| GET | `/documents/{id}` | Get document details |
| DELETE | `/documents/{id}` | Delete document |

## CLI

```sh
uv run python -m rag_system.adapter.inbound.cli.ingest_cli ingest --file document.txt
uv run python -m rag_system.adapter.inbound.cli.ingest_cli query --text "Your question"
```

## Docker

```sh
make build     # docker compose build
make up        # docker compose up -d
make down      # docker compose down
```

Four services: `app` (uvicorn :8000), `frontend` (Next.js :3000), `qdrant` (:6333), `postgres` (:5432).

## Tech stack

- **Python** 3.12+, uv, ruff strict, mypy strict
- **OpenRouter** for LLM + embeddings (swap without code changes)
- **Qdrant** vector store
- **PostgreSQL** document store (auto-migrates on first connection)
- **Cohere** reranker (available but not wired in Container by default)
- **Next.js 15** frontend with Tailwind CSS v4, next-auth, Radix UI

## Settings

All config via `.env`. See `.env.example` for required keys.

**Key detail**: `settings.py` reads `OPENROUTER_MODEL` (not `OPENROUTER_LLM_MODEL` as in `.env.example`).

## Testing

- Unit tests mock `Container` services with `unittest.mock.patch.object` + `AsyncMock`
- Integration tests need Qdrant + PostgreSQL running; skip on 401 if API key missing
- `pytest` with `asyncio_mode = auto` — no `@pytest.mark.asyncio` needed
