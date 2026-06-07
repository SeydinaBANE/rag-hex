# config

Configuration et composition root. C'est ici que tout se câble.

## Fichiers

| Fichier | Rôle |
|---|---|
| `settings.py` | `Settings` (pydantic-settings) — lit `.env` |
| `container.py` | `Container` — DI container, câble tous les adaptateurs |

## Settings

```python
class Settings(BaseSettings):
    openrouter_api_key: str        # OPENROUTER_API_KEY
    openrouter_llm_model: str      # OPENROUTER_MODEL (alias)
    openrouter_embedding_model: str
    openrouter_base_url: str       # https://openrouter.ai/api/v1
    qdrant_host: str / qdrant_port: int
    qdrant_collection: str         # rag_documents
    postgres_user / password / db / host / port
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 5
    use_reranker: bool = False
```

**Alias important** : `openrouter_llm_model` lit `OPENROUTER_MODEL` (pas `OPENROUTER_LLM_MODEL`). Voir `.env.example` pour la différence.

Les propriétés calculées :
- `qdrant_url` → `http://{host}:{port}`
- `database_url` → `postgresql://{user}:{password}@{host}:{port}/{db}`

## Container (DI)

```python
class Container:
    def __init__(self, settings: Settings)
```

Propriétés lazy (création au premier accès) :
- `embedder` → `OpenRouterEmbedder`
- `retriever` → `QdrantRetriever`
- `llm` → `OpenRouterLLM`
- `document_store` → `PostgresDocumentStore`
- `reranker` → ❌ retourne `None` (jamais initialisé)
- `query_service` → `QueryService(embedder, retriever, llm, reranker)`
- `ingestion_service` → `IngestionService(embedder, document_store, retriever)`

### Tester avec le Container

```python
from unittest.mock import AsyncMock, patch

@patch.object(Container, "query_service")
def test_query(mock_service: AsyncMock):
    mock_service.query = AsyncMock(return_value=QueryResult(query="test", answer="ok"))
    response = client.post("/query", json={"text": "test"})
```
