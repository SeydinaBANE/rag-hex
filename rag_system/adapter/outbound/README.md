# adapter/outbound

Connecteurs vers les services externes. Chaque dossier implémente un port du domaine.

| Dossier | Port | Provider |
|---|---|---|
| `embedding/` | EmbedderPort | OpenRouter |
| `llm/` | LLMPort | OpenRouter |
| `retrieval/` | RetrieverPort | Qdrant, InMemory |
| `reranker/` | RerankerPort | Cohere |
| `storage/` | DocumentStorePort | PostgreSQL |
