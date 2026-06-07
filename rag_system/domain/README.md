# domain

Cœur hexagonal — zéro dépendance externe, zéro import framework, zéro IO.

Cette couche contient toute la logique métier du RAG : les modèles de données, les contrats d'interface, et l'orchestration.

## Modules

| Module | Rôle |
|---|---|
| `model/` | Dataclasses pures : `Document`, `Chunk`, `ChunkMetadata`, `Embedding`, `Query`, `SearchResult`, `QueryResult` |
| `port/inbound/` | ABCs des use cases : `QueryUseCase`, `IngestionUseCase` |
| `port/outbound/` | ABCs des services externes : `EmbedderPort`, `RetrieverPort`, `LLMPort`, `DocumentStorePort`, `RerankerPort` |
| `service/` | Orchestration métier : `QueryService`, `IngestionService` |

## Règle absolue

```python
# ✅ OK — dépendances internes uniquement
from rag_system.domain.model.document import Document
from rag_system.domain.port.outbound.retriever_port import RetrieverPort

# ❌ INTERDIT — pas d'import externe dans domain/
import httpx  # non
from fastapi import FastAPI  # non
```

Le répertoire `domain/` doit pouvoir être importé sans que `httpx`, `fastapi`, `qdrant-client`, ou `psycopg` soient installés.
