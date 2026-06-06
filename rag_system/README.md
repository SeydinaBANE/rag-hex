# rag_system

Implémentation hexagonale (ports & adapters) d'un moteur RAG.

## Structure

| Couche | Contenu | Dépendances externes |
|---|---|---|
| `domain/model/` | Document, Chunk, Embedding, Query, SearchResult | Aucune |
| `domain/port/` | ABCs : QueryUseCase, IngestionUseCase, EmbedderPort, RetrieverPort, LLMPort, DocumentStorePort, RerankerPort | Aucune |
| `domain/service/` | QueryService, IngestionService | Ports uniquement |
| `adapter/outbound/` | OpenRouterLLM, OpenRouterEmbedder, QdrantRetriever, CohereReranker, PostgresDocumentStore, InMemoryRetriever | httpx, qdrant-client, psycopg |
| `adapter/inbound/` | FastAPI router (`/query`, `/ingest`, `/health`), Typer CLI | fastapi, typer |
| `config/` | Settings (pydantic-settings), Container DI | pydantic-settings |

## Règles

- **Domaine pur** : zéro import externe, zéro IO
- **Ports** : uniquement des ABCs, aucune implémentation
- **Services** : orchestration pure, dépendent uniquement des ports
- **Adaptateurs** : implémentent les ports, contiennent toute l'infra (HTTP, DB, etc.)
- **Container** : Composition Root, tout le câblage DI au même endroit

## Flux

**Query** : `POST /query` → QueryService → RetrieverPort.search() → (RerankerPort.rerank()) → LLMPort.generate() → réponse

**Ingestion** : `POST /ingest` → IngestionService → chunk → EmbedderPort.embed_batch() → DocumentStorePort.store()
