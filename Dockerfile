FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app/.venv .venv
COPY rag_system/ rag_system/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "rag_system.adapter.inbound.api.router:app", "--host", "0.0.0.0", "--port", "8000"]
