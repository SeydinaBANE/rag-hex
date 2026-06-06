# adapter/inbound/api

API REST FastAPI.

| Route | Méthode | Description |
|---|---|---|
| `/health` | GET | Liveness check |
| `/query` | POST | Question au RAG |
| `/ingest` | POST | Ingestion d'un document |

- `router.py` — définition des routes
- `schemas.py` — Pydantic request/response
