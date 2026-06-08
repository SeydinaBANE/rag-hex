# rag-hex — RAG system with hexagonal architecture

## Package manager

```sh
uv sync              # install all deps (including dev)
uv lock              # lock after changing pyproject.toml
```

## Required command order

```sh
make lint            # ruff check rag_system/ tests/
make typecheck       # mypy --strict --no-warn-unused-ignores -p rag_system
make test-unit       # pytest tests/unit/ --cov=rag_system
make all             # lint -> typecheck -> test-unit (in this order)
make precommit       # pre-commit run --all-files (ruff, mypy, prettier, eslint)
```

## Single-package / focused

```sh
uv run pytest tests/unit/adapter/test_api_router.py -x
uv run pytest tests/unit/service/test_query_service.py -x
uv run mypy --strict -p rag_system.config.settings  # single module
uv run ruff check rag_system/adapter/inbound/api/router.py
uv run ruff format rag_system/ tests/
```

## Architecture

```
rag_system/
  domain/              ← pure Python, zero external deps
    model/             ← dataclasses (Document, Chunk, Query, Embedding)
    exceptions.py      ← EmbeddingError, LLMError, RetrievalError (all extend RagError)
    port/inbound/      ← ABCs: QueryUseCase, IngestionUseCase
    port/outbound/     ← ABCs: EmbedderPort, RetrieverPort, LLMPort, DocumentStorePort, RerankerPort
                         All ports expose: ping() -> bool, close() -> None
    service/           ← orchestration (QueryService, IngestionService)
  adapter/
    inbound/api/       ← FastAPI routes + pydantic schemas
    inbound/cli/       ← typer CLI for batch ingestion
    outbound/          ← concrete adapters (OpenRouter, Qdrant, PostgreSQL, Cohere)
  config/
    settings.py        ← pydantic-settings (reads .env)
    container.py       ← DI container (lazy singleton properties + startup/shutdown)
```

**Key: `container.py` wires everything.** Unit tests mock `Container` services via `patch.object`.

## Settings quirks

- `.env` is gitignored; copy `.env.example` → `.env`
- `settings.py` aliases `OPENROUTER_MODEL` (not `OPENROUTER_LLM_MODEL`) for the LLM model
- `ENVIRONMENT=production` enables fail-fast startup validation (refuses to start without `OPENROUTER_API_KEY`)
- `ALLOWED_ORIGINS` is a list (comma-separated); defaults to `http://localhost:3000`
- The `reranker` property in `Container` always returns `None` (CohereReranker exists but is never wired)

## Entrypoints

| Layer | CMD |
|---|---|
| API server | `gunicorn -w 4 -k uvicorn.workers.UvicornWorker ... rag_system.adapter.inbound.api.router:app` |
| CLI | `uv run python -m rag_system.adapter.inbound.cli.ingest_cli` |

## API endpoints

| Method | Route | Notes |
|---|---|---|
| GET | `/health` | Liveness — always 200 |
| GET | `/readiness` | Deep check: pings Postgres + Qdrant → 503 if degraded |
| POST | `/query` | RAG query |
| POST | `/query/stream` | SSE streaming |
| POST | `/ingest` | Ingest document |
| GET | `/documents` | Paginated list (`?limit=50&offset=0`) |
| GET | `/documents/{id}` | Document detail + chunks |
| DELETE | `/documents/{id}` | Delete document + vectors |

## Error handling

Domain exceptions flow: adapter raises typed error → FastAPI exception handler maps to HTTP code:
- `EmbeddingError` → 503
- `LLMError` → 502
- `RetrievalError` → 503
- `RagError` (base) → 500

## Testing quirks

- `asyncio_mode = auto` — no need for `@pytest.mark.asyncio`
- Unit tests: fast, no services needed, mock `Container.*` with `AsyncMock`
- Postgres store mocks: use `MagicMock` for pool (sync context manager) + `AsyncMock` for cursor
- Integration tests: need Qdrant + PostgreSQL running; skip on 401 if `OPENROUTER_API_KEY` missing
- CI: 4 parallel jobs — `quality` (lint+typecheck), `test` (unit+coverage), `frontend` (tsc+eslint), `docker` (build)

## Docker

```sh
make build    # docker compose build
make up       # docker compose up -d
make down     # docker compose down
make rebuild  # down -> build -> up
make logs     # docker compose logs -f
make health   # curl /health
make readiness  # curl /readiness
```

Four services: `frontend` (Next.js :3000), `app` (gunicorn :8000), `qdrant` (:6333), `postgres` (:5432).

## Pre-commit hooks

Runs on every commit: ruff (lint+fix), ruff-format, mypy (with psycopg + psycopg-pool stubs), prettier (frontend), eslint (frontend).

## Toolchain

- **Python** 3.12+, strict mypy, ruff (line-length 100, double quotes)
- **Gunicorn** 4 workers + UvicornWorker, non-root Docker user (`appuser`)
- **OpenRouter** for LLM + embeddings (not direct OpenAI/Anthropic)
- **Qdrant** vector store, **PostgreSQL** document store, **Cohere** reranker (unwired)
- **Frontend**: Next.js 15 (`frontend/`), typescript, tailwind v4, prettier
