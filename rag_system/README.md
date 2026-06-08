# rag_system — RAG engine (hexagonal)

Moteur RAG en architecture hexagonale (ports & adapters). Le domaine est pur Python, sans dépendance externe. Toute l'infrastructure vit dans les adaptateurs.

## Structure

| Couche | Contenu | Dépendances |
|---|---|---|
| `domain/model/` | `Document`, `Chunk`, `Embedding`, `Query`, `SearchResult` | Aucune |
| `domain/exceptions.py` | `RagError`, `EmbeddingError`, `LLMError`, `RetrievalError` | Aucune |
| `domain/port/inbound/` | `QueryUseCase`, `IngestionUseCase` | ABCs uniquement |
| `domain/port/outbound/` | `EmbedderPort`, `RetrieverPort`, `LLMPort`, `DocumentStorePort`, `RerankerPort` | ABCs uniquement |
| `domain/service/` | `QueryService`, `IngestionService` | Ports uniquement |
| `adapter/outbound/` | `OpenRouterLLM`, `OpenRouterEmbedder`, `QdrantRetriever`, `CohereReranker`, `PostgresDocumentStore`, `InMemoryRetriever` | httpx, qdrant-client, psycopg |
| `adapter/inbound/` | FastAPI router (`/query`, `/ingest`, `/health`, `/readiness`), Typer CLI | fastapi, typer |
| `config/` | `Settings` (pydantic-settings), `Container` (DI) | pydantic-settings |

## Principes

- **Domaine pur** : zéro import externe, zéro IO, zéro side effect
- **Ports** : uniquement des classes ABC, avec `ping() -> bool` et `close() -> None` sur tous les ports outbound
- **Services** : orchestration pure, dépendent uniquement des ports
- **Adaptateurs** : implémentent les ports, contiennent toute l'infra (HTTP, DB)
- **Container** : Composition Root unique, `startup()` / `shutdown()` via lifespan FastAPI

## Flux

### Query
```
POST /query → QueryService.query()
  → EmbedderPort.embed(query.text)
  → RetrieverPort.search(embedding)
  → (RerankerPort.rerank(query.text, results))
  → LLMPort.generate(context=results, prompt=query.text)
  → QueryResult(answer, results)
```

### Ingestion
```
POST /ingest → IngestionService.ingest(document)
  → chunk document (chunk_size=512, overlap=64)
  → EmbedderPort.embed_batch(chunks)
  → DocumentStorePort.store(document + chunks)
  → RetrieverPort.store_chunks(chunks)
```

## Gestion des erreurs

Les adaptateurs lèvent des exceptions typées du domaine, catchées par les handlers FastAPI :

```
OpenRouterEmbedder → EmbeddingError → HTTP 503
OpenRouterLLM      → LLMError       → HTTP 502
QdrantRetriever    → RetrievalError → HTTP 503
```

## Contrat hexagonal

```
   ┌─────────────────────────────┐
   │       inbound/api           │  ← FastAPI / Typer
   ├─────────────────────────────┤
   │    domain/service           │  ← orchestration pure
   ├─────────────────────────────┤
   │      domain/port            │  ← ABCs (contrats)
   ├──────────────┬──────────────┤
   │ outbound/llm │ outbound/    │
   │ outbound/    │ retrieval/   │
   │ embedding/   │ storage/     │
   └──────────────┴──────────────┘
```

## Remarques

- Le `RerankerPort` (Cohere) existe mais n'est pas câblé dans le `Container` — `container.reranker` retourne `None`
- Les adaptateurs `outbound/` utilisent `httpx.AsyncClient` pour les appels HTTP et gèrent leur propre cycle de vie via `close()`
- Le `PostgresDocumentStore` auto-migre ses tables (`documents`, `chunks`) au premier appel et expose `ping()` pour les health checks
- Le `QdrantRetriever` implémente la recherche vectorielle via `query_points()` et expose `ping()` via `get_collections()`
- `InMemoryRetriever` est un stub de test (scoring par overlap de mots) — jamais utilisé en production
