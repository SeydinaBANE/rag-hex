# rag_system — RAG engine (hexagonal)

Moteur RAG en architecture hexagonale (ports & adapters). Le domaine est pur Python, sans dépendance externe. Toute l'infrastructure vit dans les adaptateurs.

## Structure

| Couche | Contenu | Dépendances |
|---|---|---|
| `domain/model/` | `Document`, `Chunk`, `Embedding`, `Query`, `SearchResult` | Aucune |
| `domain/port/inbound/` | `QueryUseCase`, `IngestionUseCase` | ABCs uniquement |
| `domain/port/outbound/` | `EmbedderPort`, `RetrieverPort`, `LLMPort`, `DocumentStorePort`, `RerankerPort` | ABCs uniquement |
| `domain/service/` | `QueryService`, `IngestionService` | Ports uniquement |
| `adapter/outbound/` | `OpenRouterLLM`, `OpenRouterEmbedder`, `QdrantRetriever`, `CohereReranker`, `PostgresDocumentStore`, `InMemoryRetriever` | httpx, qdrant-client, psycopg |
| `adapter/inbound/` | FastAPI router (`/query`, `/ingest`, `/health`), Typer CLI | fastapi, typer |
| `config/` | `Settings` (pydantic-settings), `Container` (DI) | pydantic-settings |

## Principes

- **Domaine pur** : zéro import externe, zéro IO, zéro side effect
- **Ports** : uniquement des classes ABC, aucune implémentation
- **Services** : orchestration pure, dépendent uniquement des ports
- **Adaptateurs** : implémentent les ports, contiennent toute l'infra (HTTP, DB)
- **Container** : Composition Root unique, tout le câblage DI au même endroit

## Flux

### Query
```
POST /query → QueryService.search()
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
  → RetrieverPort.upsert_chunk(chunk_id, embedding, payload)
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
- Les adaptateurs `outbound/` utilisent `httpx.AsyncClient` pour les appels HTTP et gèrent leur propre cycle de vie (`close()`)
- Le `PostgresDocumentStore` auto-migre ses tables (`documents`, `chunks`) au premier appel
- Le `QdrantRetriever.search()` est actuellement un stub qui retourne `[]` — l'implémentation vectorielle complète doit utiliser `ensure_collection()` + `upsert_chunk()` avant la recherche
