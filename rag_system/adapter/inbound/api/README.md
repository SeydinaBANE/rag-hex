# adapter/inbound/api

API REST FastAPI. Point d'entrée principal pour les clients HTTP.

## Routes

| Méthode | Route | Request | Response | Description |
|---|---|---|---|---|
| GET | `/health` | — | `{status: "ok"}` | Liveness check |
| POST | `/query` | `{text, top_k?, filters?}` | `{query, answer, results[]}` | RAG query |
| POST | `/query/stream` | `{text, top_k?, filters?}` | `text/event-stream` | SSE streaming |
| POST | `/ingest` | `{document_id, content, metadata?}` | `{status, document_id}` | Document ingestion |
| GET | `/documents` | — | `{documents[]}` | List documents |
| GET | `/documents/{id}` | — | `{id, content, metadata, chunks[]}` | Document detail |
| DELETE | `/documents/{id}` | — | `{status, document_id}` | Delete document |

## Architecture

```python
# router.py — global singleton Container
settings = Settings()
container = Container(settings)
app = FastAPI(title="RAG Hex", version="0.1.0")
```

Le `Container` est créé au niveau module (singleton global). Les tests unitaires mockent ses propriétés avec `@patch.object(Container, "query_service")`.

## Streaming

Le endpoint `/query/stream` utilise `StreamingResponse` avec Server-Sent Events :

```
data: {"type": "token", "data": "réponse..."}
data: [DONE]
```

Les tokens arrivent un par un depuis `OpenRouterLLM.generate_stream()`.

## Schemas

Tous les schemas request/response sont dans `schemas.py` (Pydantic BaseModel) :

- `QueryRequest` : text (str), top_k (int=5), filters (dict\|None)
- `QueryResponse` : query (str), answer (str\|None), results (SearchResultItem[])
- `IngestRequest` : document_id (str), content (str), metadata (dict=empty)
- `DocumentSummary` / `DocumentDetail` / `ChunkDetail` : CRUD documents
