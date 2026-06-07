# rag-hex — RAG system with hexagonal architecture

## Package manager

```sh
uv sync              # install all deps (including dev)
uv lock              # lock after changing pyproject.toml
```

## Required command order

```sh
make lint            # ruff check rag_system/ tests/
make typecheck       # mypy --strict -p rag_system
make test            # pytest tests/ (unit + integration)
make all             # lint -> typecheck -> test (in this order)
make precommit       # pre-commit run --all-files (ruff, mypy, prettier, eslint)
```

Combine: `make lint typecheck test` or `make all`.

## Single-package / focused

```sh
make test-unit       # pytest tests/unit/
make test-integration  # pytest tests/integration/ (needs infra)
uv run pytest tests/unit/adapter/test_api_router.py -x
uv run mypy --strict -p rag_system.config.settings  # single module
uv run ruff check rag_system/adapter/inbound/api/router.py
uv run ruff format rag_system/ tests/
```

## Architecture

```
rag_system/
  domain/              ← pure Python, zero external deps
    model/             ← dataclasses (Document, Chunk, Query, Embedding)
    port/inbound/      ← ABCs: QueryUseCase, IngestionUseCase
    port/outbound/     ← ABCs: EmbedderPort, RetrieverPort, LLMPort, ...
    service/           ← orchestration (QueryService, IngestionService)
  adapter/
    inbound/api/       ← FastAPI routes + pydantic schemas
    inbound/cli/       ← typer CLI for batch ingestion
    outbound/          ← concrete adapters (OpenRouter, Qdrant, PostgreSQL, Cohere)
  config/
    settings.py        ← pydantic-settings (reads .env)
    container.py       ← DI container (lazy singleton properties)
  adapter/outbound/storage/  ← lacks __init__.py
```

**Key: `container.py` wires everything.** Unit tests mock `Container` services via `patch.object`.

## Settings quirks

- `.env` is gitignored; copy `.env.example` → `.env`
- `settings.py` aliases `OPENROUTER_MODEL` (not `OPENROUTER_LLM_MODEL` from `.env.example`) — if using `.env.example`, rename the key
- The `reranker` property in `Container` always returns `None` (CohereReranker exists but is never wired)

## Entrypoints

| Layer | CMD |
|---|---|
| API server | `uvicorn rag_system.adapter.inbound.api.router:app` (Dockerfile CMD) |
| CLI | `uv run python -m rag_system.adapter.inbound.cli.ingest_cli` |

## Testing quirks

- `asyncio_mode = auto` — no need for `@pytest.mark.asyncio`
- Unit tests: fast, no services needed, mock `Container.*` with `AsyncMock`
- Integration tests: need Qdrant + PostgreSQL running; skip on 401 if `OPENROUTER_API_KEY` missing
- CI spins up Qdrant + PostgreSQL as `services:` for the test job

## Docker

```sh
make build    # docker compose build
make up       # docker compose up -d
make down     # docker compose down
make rebuild  # down -> build -> up
```

Four services: `frontend` (Next.js), `app` (uvicorn), `qdrant`, `postgres`.

## Pre-commit hooks

Runs on every commit: ruff (lint+fix), ruff-format, mypy, prettier (frontend), eslint (frontend). Also `uv run pre-commit run --all-files`.

## Toolchain

- **Python** 3.12+, strict mypy, ruff (line-length 100, double quotes)
- **OpenRouter** for LLM + embeddings (not direct OpenAI/Anthropic)
- **Qdrant** vector store, **PostgreSQL** document store, **Cohere** reranker (unwired)
- **Frontend**: Next.js 15 (`frontend/`), typescript, tailwind v4, prettier
- CI: lint + typecheck → unit tests → docker build (three parallel jobs)
