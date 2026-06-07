# adapter/outbound

Connecteurs vers les services externes. Chaque dossier implémente un port du domaine.

| Dossier | Port implémenté | Provider |
|---|---|---|
| `embedding/` | `EmbedderPort` | OpenRouter `/embeddings` |
| `llm/` | `LLMPort` | OpenRouter `/chat/completions` |
| `retrieval/` | `RetrieverPort` | Qdrant (prod), InMemory (tests) |
| `reranker/` | `RerankerPort` | Cohere `/rerank` |
| `storage/` | `DocumentStorePort` | PostgreSQL |

## Conventions

- Chaque adaptateur prend sa configuration en `__init__` (pas de lecture directe de `.env`)
- Tous exposent une méthode `async close()` pour libérer les ressources
- Les clients HTTP utilisent `httpx.AsyncClient` avec `raise_for_status()`
- Le `Container` dans `config/container.py` instancie et câble chaque adaptateur

## État actuel

| Adaptateur | Statut | Note |
|---|---|---|
| OpenRouterEmbedder | ✅ Production | Fonctionnel |
| OpenRouterLLM | ✅ Production | Streaming inclus |
| QdrantRetriever | ⚠️ Partiel | `search()` retourne `[]` — voir le stub |
| InMemoryRetriever | ✅ Tests | Recherche textuelle simple |
| PostgresDocumentStore | ✅ Production | Auto-migration des tables |
| CohereReranker | ✅ Disponible | Non câblé dans le Container |
