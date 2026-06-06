# adapter

Implémentations concrètes des ports. Toute l'infra (HTTP, DB, CLI, API) vit ici.

- `inbound/` — points d'entrée : API REST, CLI
- `outbound/` — connecteurs externes : LLM, embedding, vector store, base de données, reranking
